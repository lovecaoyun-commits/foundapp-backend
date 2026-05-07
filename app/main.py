from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
import json
import hashlib
import time
import re
from typing import Dict, List
from contextlib import contextmanager

app = FastAPI(title="FoundApp API", version="2.0.0", root_path="/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "/tmp/foundapp.db"

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        # Notify user they connected
        await websocket.send_json({"type": "connected", "user_id": user_id})
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, phone TEXT UNIQUE, nickname TEXT DEFAULT '', avatar TEXT DEFAULT '', gender INTEGER DEFAULT 0, birthday TEXT DEFAULT '', bio TEXT DEFAULT '', location TEXT DEFAULT '', password_hash TEXT DEFAULT '', verified INTEGER DEFAULT 0, vip_expire TEXT, created_at REAL, updated_at REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS matches (match_id TEXT PRIMARY KEY, user_id TEXT, target_id TEXT, status TEXT DEFAULT 'matched', created_at REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (msg_id TEXT PRIMARY KEY, match_id TEXT, sender_id TEXT, receiver_id TEXT, content TEXT, msg_type TEXT DEFAULT 'text', created_at REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS moments (moment_id TEXT PRIMARY KEY, user_id TEXT, content TEXT DEFAULT '', images TEXT DEFAULT '[]', likes TEXT DEFAULT '[]', comments TEXT DEFAULT '[]', created_at REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS wallets (user_id TEXT PRIMARY KEY, coins INTEGER DEFAULT 0, vip_expire TEXT, updated_at REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sms_codes (phone TEXT PRIMARY KEY, code TEXT, created_at REAL)''')
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = get_conn()
    try:
        yield conn.cursor()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

init_db()

from app.routers import utils as utils_router
from app.routers import trtc as trtc_router
app.include_router(utils_router.router)
app.include_router(trtc_router.router)

def make_token(user_id):
    return hashlib.md5(f"{user_id}:{time.time()}".encode()).hexdigest()

def validate_phone(p):
    return bool(re.match(r'^1[3-9]\d{9}$', p))

# === WEBSOCKET ===
@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get('type', '')
                
                if msg_type == 'ping':
                    await websocket.send_json({"type": "pong"})
                
                elif msg_type == 'chat':
                    # Save and forward chat message
                    receiver_id = msg.get('receiver_id', '')
                    content = msg.get('content', '')
                    conv_id = msg.get('conv_id', '')
                    msg_id = msg.get('msg_id', f"ws_{int(time.time()*1000)}")
                    msg_type_ = msg.get('msg_type', 'text')
                    
                    # Save to database
                    conn = get_conn()
                    c = conn.cursor()
                    c.execute('INSERT INTO messages (msg_id, match_id, sender_id, receiver_id, content, msg_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                              (msg_id, conv_id, user_id, receiver_id, content, msg_type_, time.time()))
                    conn.commit()
                    conn.close()
                    
                    # Send confirmation to sender
                    await websocket.send_json({
                        "type": "message_sent",
                        "msg_id": msg_id,
                        "status": "delivered"
                    })
                    
                    # Forward to receiver if online
                    await manager.send_to_user(receiver_id, {
                        "type": "new_message",
                        "msg_id": msg_id,
                        "sender_id": user_id,
                        "receiver_id": receiver_id,
                        "content": content,
                        "msg_type": msg_type_,
                        "conv_id": conv_id,
                        "timestamp": int(time.time() * 1000)
                    })
                
                elif msg_type == 'typing':
                    receiver_id = msg.get('receiver_id', '')
                    conv_id = msg.get('conv_id', '')
                    await manager.send_to_user(receiver_id, {
                        "type": "typing",
                        "user_id": user_id,
                        "conv_id": conv_id
                    })
                
                elif msg_type == 'read':
                    sender_id = msg.get('sender_id', '')
                    conv_id = msg.get('conv_id', '')
                    await manager.send_to_user(sender_id, {
                        "type": "read",
                        "conv_id": conv_id,
                        "reader_id": user_id
                    })
                
                elif msg_type == 'fetch_offline':
                    # Send offline messages
                    conn = get_conn()
                    c = conn.cursor()
                    c.execute('SELECT * FROM messages WHERE receiver_id=? AND created_at > ? ORDER BY created_at ASC',
                              (user_id, time.time() - 86400))
                    msgs = c.fetchall()
                    conn.close()
                    for m in msgs:
                        await websocket.send_json({
                            "type": "new_message",
                            "msg_id": m['msg_id'],
                            "sender_id": m['sender_id'],
                            "receiver_id": m['receiver_id'],
                            "content": m['content'],
                            "msg_type": m['msg_type'],
                            "conv_id": m['match_id'],
                            "timestamp": int(m['created_at'] * 1000)
                        })
            
            except json.JSONDecodeError:
                pass
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# === REST API ===
@app.post("/auth/login")
async def login(req: dict):
    phone, code = req.get('phone',''), req.get('code','')
    if not validate_phone(phone): return {"code": 400, "message": "ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂºÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂ ÃÂÃÂÃÂÃÂ¼ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ¼ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ©ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ¯ÃÂÃÂÃÂÃÂ¯"}
    if code != "000000": return {"code": 400, "message": "ÃÂÃÂÃÂÃÂ©ÃÂÃÂÃÂÃÂªÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ¯ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ§ÃÂÃÂÃÂÃÂ ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ©ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ¯ÃÂÃÂÃÂÃÂ¯"}
    user_id = hashlib.md5(phone.encode()).hexdigest()[:16]
    
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE phone=?', (phone,))
    user = c.fetchone()
    
    if not user:
        c.execute('INSERT INTO users (user_id, phone, created_at, updated_at) VALUES (?, ?, ?, ?)', 
                   (user_id, phone, time.time(), time.time()))
        c.execute('INSERT INTO wallets (user_id, coins, updated_at) VALUES (?, 0, ?)', 
                   (user_id, time.time()))
        conn.commit()
        c.execute('SELECT * FROM users WHERE phone=?', (phone,))
        user = c.fetchone()
    
    c.execute('SELECT coins FROM wallets WHERE user_id=?', (user['user_id'],))
    w = c.fetchone()
    conn.close()
    
    return {"code": 0, "data": {"user_id": user['user_id'], "phone": user['phone'], "nickname": user['nickname'], "avatar": user['avatar'], "access_token": make_token(user['user_id']), "expires_in": 604800, "coins": w['coins'] if w else 0}}

@app.post("/auth/send_code")
async def send_code(phone: str):
    if not validate_phone(phone): return {"code": 400, "message": "ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂºÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂ ÃÂÃÂÃÂÃÂ¼ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ¼ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ©ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ¯ÃÂÃÂÃÂÃÂ¯"}
    return {"code": 0, "message": "ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ©ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ", "data": {"code": "000000"}}

@app.get("/user/profile/{user_id}")
async def get_profile(user_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    u = c.fetchone()
    result = {"code": 0, "data": dict(u)} if u else {"code": 404, "message": "ÃÂÃÂÃÂÃÂ§ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ¤ÃÂÃÂÃÂÃÂ¸ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ­ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨"}
    conn.close()
    return result

@app.post("/user/profile/update")
async def update_profile(user_id: str, nickname: str = "", avatar: str = "", gender: int = 0, birthday: str = "", bio: str = "", location: str = ""):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET nickname=?, avatar=?, gender=?, birthday=?, bio=?, location=?, updated_at=? WHERE user_id=?', 
               (nickname, avatar, gender, birthday, bio, location, time.time(), user_id))
    conn.commit()
    rows = c.rowcount
    conn.close()
    return {"code": 0, "message": "ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ´ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ°ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ" if rows > 0 else "ÃÂÃÂÃÂÃÂ§ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ¤ÃÂÃÂÃÂÃÂ¸ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ­ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨"}

@app.get("/match/recommendations")
async def get_recommendations(user_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT user_id, phone, nickname, avatar, gender, bio, location FROM users WHERE user_id != ? AND user_id NOT IN (SELECT target_id FROM matches WHERE user_id = ?) LIMIT 20', (user_id, user_id))
    rows = c.fetchall()
    conn.close()
    return {"code": 0, "data": {"users": [dict(r) for r in rows], "total": len(rows)}}

@app.post("/match/like")
async def like_user(user_id: str, target_id: str):
    match_id = hashlib.md5(f"{user_id}:{target_id}".encode()).hexdigest()[:16]
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO matches (match_id, user_id, target_id, created_at) VALUES (?, ?, ?, ?)', 
               (match_id, user_id, target_id, time.time()))
    conn.commit()
    conn.close()
    return {"code": 0, "message": "ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ²ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂ¬ÃÂÃÂÃÂÃÂ¢", "data": {"match_id": match_id}}

@app.post("/match/dislike")
async def dislike_user(user_id: str, target_id: str):
    return {"code": 0, "message": "ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ²ÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ³ÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ¿ÃÂÃÂÃÂÃÂ"}

@app.get("/match/list")
async def get_matches(user_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM matches WHERE user_id=? OR target_id=? ORDER BY created_at DESC', (user_id, user_id))
    rows = c.fetchall()
    conn.close()
    return {"code": 0, "data": {"matches": [dict(r) for r in rows], "total": len(rows)}}

@app.get("/chat/messages/{match_id}")
async def get_messages(match_id: str, page: int = 1, size: int = 20):
    offset = (page - 1) * size
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM messages WHERE match_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?', (match_id, size, offset))
    rows = c.fetchall()
    conn.close()
    return {"code": 0, "data": {"messages": [dict(r) for r in rows], "total": len(rows)}}

@app.post("/chat/messages/send")
async def send_message(match_id: str, sender_id: str, receiver_id: str = "", content: str = "", msg_type: str = "text"):
    msg_id = hashlib.md5(f"{match_id}:{sender_id}:{content}:{time.time()}".encode()).hexdigest()[:16]
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO messages (msg_id, match_id, sender_id, receiver_id, content, msg_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)', 
               (msg_id, match_id, sender_id, receiver_id, content, msg_type, time.time()))
    conn.commit()
    conn.close()
    
    # Try to notify via WebSocket
    if receiver_id:
        try:
            await manager.send_to_user(receiver_id, {
                "type": "new_message",
                "msg_id": msg_id,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": content,
                "msg_type": msg_type,
                "conv_id": match_id,
                "timestamp": int(time.time() * 1000)
            })
        except:
            pass
    
    return {"code": 0, "message": "ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ©ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ", "data": {"msg_id": msg_id}}

@app.get("/moments/list")
async def get_moments(page: int = 1, size: int = 20):
    offset = (page - 1) * size
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT m.*, u.nickname, u.avatar FROM moments m JOIN users u ON m.user_id=u.user_id ORDER BY m.created_at DESC LIMIT ? OFFSET ?', (size, offset))
    rows = c.fetchall()
    conn.close()
    return {"code": 0, "data": {"moments": [dict(r) for r in rows], "total": len(rows)}}

@app.post("/moments/publish")
async def publish(user_id: str, content: str = "", images: str = "[]"):
    moment_id = hashlib.md5(f"{user_id}:{content}:{time.time()}".encode()).hexdigest()[:16]
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO moments (moment_id, user_id, content, images, created_at) VALUES (?, ?, ?, ?, ?)', 
               (moment_id, user_id, content, images, time.time()))
    conn.commit()
    conn.close()
    return {"code": 0, "message": "ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ¸ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ", "data": {"moment_id": moment_id}}

@app.post("/moments/like")
async def like_moment(moment_id: str, user_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT likes FROM moments WHERE moment_id=?', (moment_id,))
    r = c.fetchone()
    if r:
        likes = json.loads(r['likes']) if r['likes'] else []
        if user_id not in likes: likes.append(user_id)
        c.execute('UPDATE moments SET likes=? WHERE moment_id=?', (json.dumps(likes), moment_id))
        conn.commit()
    conn.close()
    return {"code": 0, "message": "ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ²ÃÂÃÂÃÂÃÂ§ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¹ÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂµÃÂÃÂÃÂÃÂ"}


// === ANDROID MOMENTS FEED (compatible with FeedItem model) ===
@app.get("/api/moments/feed")
async def get_moments_feed(page: int = 1, size: int = 20):
    offset = (page - 1) * size
    conn = get_conn()
    c = conn.cursor()
    c.execute(`
        SELECT m.moment_id, m.user_id, m.content, m.images, m.likes, m.comments, m.created_at,
               u.nickname, u.avatar
        FROM moments m
        JOIN users u ON m.user_id = u.user_id
        ORDER BY m.created_at DESC
        LIMIT ? OFFSET ?
    `, (size, offset))
    rows = c.fetchall()
    conn.close()
    result = []
    for r in rows:
        try: images = json.loads(r['images']) if r['images'] else []
        except: images = []
        try:
            likes_list = json.loads(r['likes']) if r['likes'] else []
            comments_list = json.loads(r['comments']) if r['comments'] else []
        except:
            likes_list = []
            comments_list = []
        result.append({
            "id": r['moment_id'],
            "content": r['content'] or "",
            "author": {
                "id": r['user_id'],
                "nickname": r['nickname'] or "",
                "avatar": r['avatar'] or ""
            },
            "images": images,
            "likeCount": len(likes_list),
            "commentCount": len(comments_list),
            "isLiked": False,
            "createdAt": str(r['created_at']) if r['created_at'] else ""
        })
    return {"code": 0, "data": result}



// === ANDROID MOMENTS PUBLISH ===
@app.post("/api/moments")
async def publish_moment(body: dict):
    user_id = body.get("user_id", "")
    content = body.get("content", "")
    images = body.get("images", [])
    if not content and not images:
        return {"code": 1, "message": "Content is required"}
    import json
    images_str = json.dumps(images) if isinstance(images, list) else "[]"
    moment_id = hashlib.md5(f"{user_id}:{content}:{time.time()}".encode()).hexdigest()[:16]
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO moments (moment_id, user_id, content, images, created_at) VALUES (?, ?, ?, ?, ?)",
              (moment_id, user_id, content, images_str, time.time()))
    conn.commit()
    conn.close()
    return {"code": 0, "message": "Published", "data": {"id": moment_id}}

// === ANDROID MOMENTS COMMENTS ===
@app.get("/api/moments/{moment_id}/comments")
async def get_moment_comments(moment_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT comments FROM moments WHERE moment_id=?", (moment_id,))
    r = c.fetchone()
    conn.close()
    if not r or not r["comments"]:
        return {"code": 0, "data": []}
    try:
        import json
        comments = json.loads(r["comments"])
        return {"code": 0, "data": comments}
    except:
        return {"code": 0, "data": []}

@app.get("/wallet/balance")
async def get_balance(user_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM wallets WHERE user_id=?', (user_id,))
    w = c.fetchone()
    if not w:
        c.execute('INSERT INTO wallets (user_id, coins, updated_at) VALUES (?, 0, ?)', (user_id, time.time()))
        conn.commit()
        c.execute('SELECT * FROM wallets WHERE user_id=?', (user_id,))
        w = c.fetchone()
    result = {"code": 0, "data": dict(w)} if w else {"code": 404, "message": "ÃÂÃÂÃÂÃÂ©ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ±ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¤ÃÂÃÂÃÂÃÂ¸ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ­ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨"}
    conn.close()
    return result

@app.get("/wallet/recharge/packages")
async def get_packages():
    return {"code": 0, "data": {"packages": [{"id": "p1", "coins": 100, "price": 6}, {"id": "p2", "coins": 500, "price": 30, "discount": True}, {"id": "p3", "coins": 1000, "price": 58, "best_value": True}]}}

@app.post("/wallet/recharge")
async def recharge(user_id: str, package_id: str):
    coins_map = {"p1": 100, "p2": 500, "p3": 1000}
    coins = coins_map.get(package_id, 0)
    if coins > 0:
        conn = get_conn()
        c = conn.cursor()
        c.execute('UPDATE wallets SET coins=coins+?, updated_at=? WHERE user_id=?', (coins, time.time(), user_id))
        conn.commit()
        rows = c.rowcount
        conn.close()
        if rows > 0:
            return {"code": 0, "message": "ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¼ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ", "data": {"coins": coins}}
        return {"code": 1, "message": "ÃÂÃÂÃÂÃÂ§ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨ÃÂÃÂÃÂÃÂ¦ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ·ÃÂÃÂÃÂÃÂ¤ÃÂÃÂÃÂÃÂ¸ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ­ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨"}
    return {"code": 1, "message": "ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ©ÃÂÃÂÃÂÃÂ¤ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¤ÃÂÃÂÃÂÃÂ¸ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂ­ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¥ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¨"}

@app.post("/trtc/sign")
async def trtc_sign(user_id: str, room_id: str):
    sig = hashlib.md5(f"{user_id}:{room_id}:{time.time()}".encode()).hexdigest()
    return {"code": 0, "data": {"signature": sig}}

@app.get("/utils/upload/token")
async def get_upload_token():
    return {"code": 0, "data": {"token": "", "upload_url": ""}}

@app.get("/utils/areas")
async def get_areas():
    return {"code": 0, "data": []}

@app.get("/ping")


@app.get("/api/test")
async def test_route():
    return {"test": "ok", "time": "2026-05-07T02:25:16.217Z"}async def ping():
    return {"code": 0, "data": "pong"}


@app.get("/upload_token")
async def get_upload_token(filename: str = ""):
    r = utils_router.gen_upload_token(filename)
    return {"code": 0, "data": {"token": r["token"], "upload_url": r["upload_url"], "key": r["key"]}}



@app.get("/api/debug")
async def debug_endpoint():
    return {"status": "ok", "commit": "2026-05-07T02:24:22.936Z"}
@app.get("/")
async def root():
    return {"message": "FoundApp API", "version": "2.0.0"}


@app.get("/api/hello")
async def hello():
    return {"hello": "world"}
