import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models.link import Link
from models.user import User
from schemas.link import LinkCreate, LinkUpdate
from core.redis_client import RedisCache
from core.config import settings
from typing import Optional, List

class LinkService:
    @staticmethod
    def generate_short_code(length: int = 6) -> str:
        """Generate random short code"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def create_link(db: Session, link_data: LinkCreate, user_id: Optional[str] = None) -> Link:
        """Create new short link"""
        # Check if custom alias is unique
        if link_data.custom_alias:
            existing = db.query(Link).filter(
                or_(
                    Link.short_code == link_data.custom_alias,
                    Link.custom_alias == link_data.custom_alias
                )
            ).first()
            if existing:
                raise ValueError("Custom alias already exists")
            short_code = link_data.custom_alias
        else:
            # Generate unique short code
            while True:
                short_code = LinkService.generate_short_code(settings.SHORT_CODE_LENGTH)
                existing = db.query(Link).filter(Link.short_code == short_code).first()
                if not existing:
                    break
        
        # Create link
        link = Link(
            short_code=short_code,
            original_url=str(link_data.original_url),
            custom_alias=link_data.custom_alias,
            expires_at=link_data.expires_at,
            user_id=user_id
        )
        
        db.add(link)
        db.commit()
        db.refresh(link)
        
        # Cache the link
        RedisCache.set(f"link:{short_code}", {
            "original_url": link.original_url,
            "is_active": link.is_active
        })
        
        return link
    
    @staticmethod
    def get_link(db: Session, short_code: str) -> Optional[Link]:
        """Get link by short code with caching"""
        # Try cache first
        cached = RedisCache.get(f"link:{short_code}")
        if cached and cached.get("is_active"):
            # Update click count asynchronously (would use Celery in production)
            return db.query(Link).filter(Link.short_code == short_code).first()
        
        # Get from DB
        link = db.query(Link).filter(
            Link.short_code == short_code,
            Link.is_active == True
        ).first()
        
        if link and link.expires_at and link.expires_at < datetime.utcnow():
            link.is_active = False
            db.commit()
            return None
        
        return link
    
    @staticmethod
    def record_click(db: Session, link: Link):
        """Record click on link"""
        link.clicks += 1
        link.last_accessed_at = datetime.utcnow()
        db.commit()
        
        # Update cache
        RedisCache.set(f"link:{link.short_code}", {
            "original_url": link.original_url,
            "is_active": link.is_active
        })
    
    @staticmethod
    def update_link(db: Session, link: Link, link_update: LinkUpdate, user_id: str) -> Link:
        """Update link (only owner)"""
        if link.user_id != user_id:
            raise PermissionError("You don't have permission to update this link")
        
        update_data = link_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(link, field, str(value) if field == "original_url" else value)
        
        db.commit()
        db.refresh(link)
        
        # Invalidate cache
        RedisCache.delete(f"link:{link.short_code}")
        
        return link
    
    @staticmethod
    def delete_link(db: Session, link: Link, user_id: str) -> bool:
        """Delete link (only owner)"""
        if link.user_id and link.user_id != user_id:
            raise PermissionError("You don't have permission to delete this link")
        
        db.delete(link)
        db.commit()
        
        # Invalidate cache
        RedisCache.delete(f"link:{link.short_code}")
        
        return True
    
    @staticmethod
    def get_link_stats(db: Session, short_code: str) -> Optional[Link]:
        """Get link statistics"""
        return db.query(Link).filter(Link.short_code == short_code).first()
    
    @staticmethod
    def search_by_original_url(db: Session, original_url: str) -> List[Link]:
        try:
        # Используем ilike для регистронезависимого поиска
            links = db.query(Link).filter(
                Link.original_url.ilike(f"%{original_url}%"),
                Link.is_active == True
            ).all()
            return links
        except Exception as e:
            print(f"Search error: {e}")
            return []  # Всегда возвращаем список, даже пустой
    
    @staticmethod
    def cleanup_expired_links(db: Session):
        """Delete expired links"""
        expired = db.query(Link).filter(
            Link.expires_at < datetime.utcnow()
        ).all()
        
        for link in expired:
            RedisCache.delete(f"link:{link.short_code}")
            db.delete(link)
        
        db.commit()
        return len(expired)
    
    @staticmethod
    def cleanup_unused_links(db: Session, days: int = settings.DEFAULT_EXPIRY_DAYS):
        """Delete links not used for specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        unused = db.query(Link).filter(
            or_(
                Link.last_accessed_at < cutoff_date,
                and_(Link.last_accessed_at.is_(None), Link.created_at < cutoff_date)
            )
        ).all()
        
        for link in unused:
            RedisCache.delete(f"link:{link.short_code}")
            db.delete(link)
        
        db.commit()
        return len(unused)
    
    @staticmethod
    def get_expired_links_history(db: Session) -> List[Link]:
        """Get history of expired links"""
        return db.query(Link).filter(
            Link.expires_at < datetime.utcnow()
        ).all()