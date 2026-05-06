import os
import sqlite3

Base = None
engine = None
SessionLocal = None

if not Base:
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import NullPool
        Base = declarative_base()
        DATABASE_URL = os.getenv("DATABASE_URL", "")
        if DATABASE_URL:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True, poolclass=NullPool)
        else:
            # Use SQLite for local dev
            db_path = os.path.join(os.path.dirname(__file__), 'foundapp.db')
            engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except ImportError:
        pass

def get_db():
    if SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None

def init_db():
    global Base
    if Base and Base.metadata:
        # Import all models to register them
        try:
            from app.models.user import User
            from app.models.moment import Moment
            from app.models.match import Match
            from app.models.message import Message
            from app.models.transaction import VirtualCurrency, RechargeOrder
        except:
            pass
        if engine is not None:
            Base.metadata.create_all(bind=engine)
