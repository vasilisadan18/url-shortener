import time
import schedule
from app.core.database import SessionLocal
from app.services.link_service import LinkService
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_expired_links():
    """Job to cleanup expired links"""
    db = SessionLocal()
    try:
        count = LinkService.cleanup_expired_links(db)
        if count > 0:
            logger.info(f"Cleaned up {count} expired links")
    except Exception as e:
        logger.error(f"Error cleaning up expired links: {e}")
    finally:
        db.close()

def cleanup_unused_links():
    """Job to cleanup unused links"""
    db = SessionLocal()
    try:
        count = LinkService.cleanup_unused_links(db, settings.DEFAULT_EXPIRY_DAYS)
        if count > 0:
            logger.info(f"Cleaned up {count} unused links")
    except Exception as e:
        logger.error(f"Error cleaning up unused links: {e}")
    finally:
        db.close()

def start_cleanup_scheduler():
    """Start background scheduler for cleanup jobs"""
    # Run cleanup every hour
    schedule.every().hour.do(cleanup_expired_links)
    schedule.every().day.at("03:00").do(cleanup_unused_links)  # Daily at 3 AM
    
    logger.info("Cleanup scheduler started")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute