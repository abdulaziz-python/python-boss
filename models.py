from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class BannedUser(Base):
    __tablename__ = "banned_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer, ForeignKey("chats.id"))
    banned_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")
    chat = relationship("Chat")

class MutedUser(Base):
    __tablename__ = "muted_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer, ForeignKey("chats.id"))
    muted_at = Column(DateTime, default=datetime.datetime.utcnow)
    muted_until = Column(DateTime)

    user = relationship("User")
    chat = relationship("Chat")

