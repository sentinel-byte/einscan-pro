from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
from backend.database import Base

class AppConfig(Base):
    __tablename__ = "app_configs"
    key = Column(String, primary_key=True, index=True)
    value = Column(String)

class License(Base):
    __tablename__ = "licenses"
    key = Column(String, primary_key=True, index=True)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
