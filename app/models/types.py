from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, SmallInteger
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(32))
    def process_bind_param(self, value, dialect):
        if value is None: return value
        if dialect.name == 'postgresql': return value
        if isinstance(value, uuid.UUID): return value.hex
        return str(value)
    def process_result_value(self, value, dialect):
        if value is None: return value
        if not isinstance(value, uuid.UUID): return uuid.UUID(value)
        return value
