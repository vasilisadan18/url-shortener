from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Link(Base):
    __tablename__ = "links"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    short_code = Column(String, unique=True, index=True, nullable=False)
    original_url= Column(String, nullable=False)
    custom_alias=Column(String, unique=True, nullable=True)
    clicks = Column(Integer, default=0)
    created_at= Column(DateTime(timezone=True), server_default=func.now())
    updated_at= Column(DateTime(timezone=True), onupdate=func.now())
    last_accessed_at= Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    user=relationship("User", back_populates="links")