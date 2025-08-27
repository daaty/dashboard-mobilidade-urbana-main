from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Computed
from sqlalchemy.ext.declarative import declarative_base
from app.database.db import Base

class User(Base):
    __tablename__ = "dashboard_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), Computed("first_name || ' ' || last_name"), index=True)
    roles = Column(String(100), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
