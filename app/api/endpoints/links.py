from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user, get_optional_user
from app.models.user import User
from app.models.link import Link
from app.schemas.link import (
    LinkCreate, LinkResponse, LinkUpdate, 
    LinkStats, LinkSearchResult
)
from app.services.link_service import LinkService
from app.core.config import settings
from datetime import datetime

router = APIRouter()

@router.get("/search", response_model=List[LinkSearchResult])
def search_links(
    original_url: str = Query(..., description="Original URL to search for"),
    db: Session = Depends(get_db)
):
    links = LinkService.search_by_original_url(db, original_url)
    
    results = []
    for link in links:
        results.append({
            "short_code": link.short_code,
            "short_url": f"{settings.BASE_URL}/{link.short_code}",
            "original_url": link.original_url,
            "created_at": link.created_at,
            "clicks": link.clicks
        })
    
    return results

@router.get("/expired/history", response_model=List[LinkResponse])
def get_expired_links_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    links = LinkService.get_expired_links_history(db)
    user_links = [link for link in links if link.user_id == current_user.id]
    
    results = []
    for link in user_links:
        response_dict = {
            "id": link.id,
            "short_code": link.short_code,
            "original_url": link.original_url,
            "short_url": f"{settings.BASE_URL}/{link.short_code}",
            "custom_alias": link.custom_alias,
            "clicks": link.clicks,
            "created_at": link.created_at,
            "expires_at": link.expires_at,
            "is_active": link.is_active
        }
        results.append(LinkResponse.model_validate(response_dict))
    
    return results

@router.post("/cleanup/unused", status_code=status.HTTP_200_OK)
def cleanup_unused_links(
    days: int = Query(settings.DEFAULT_EXPIRY_DAYS, description="Days of inactivity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cleanup unused links"""
    count = LinkService.cleanup_unused_links(db, days)
    return {"message": f"Cleaned up {count} unused links"}

@router.post("/shorten", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_short_link(
    link_data: LinkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    try:
        link = LinkService.create_link(
            db=db,
            link_data=link_data,
            user_id=current_user.id if current_user else None
        )
        
        response_dict = {
            "id": link.id,
            "short_code": link.short_code,
            "original_url": link.original_url,
            "short_url": f"{settings.BASE_URL}/{link.short_code}",
            "custom_alias": link.custom_alias,
            "clicks": link.clicks,
            "created_at": link.created_at,
            "expires_at": link.expires_at,
            "is_active": link.is_active
        }
        
        return LinkResponse.model_validate(response_dict)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{short_code}/stats", response_model=LinkStats)
def get_link_statistics(
    short_code: str,
    db: Session = Depends(get_db)
):
    link = LinkService.get_link_stats(db, short_code)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    stats_dict = {
        "id": link.id,
        "short_code": link.short_code,
        "original_url": link.original_url,
        "short_url": f"{settings.BASE_URL}/{link.short_code}",
        "custom_alias": link.custom_alias,
        "clicks": link.clicks,
        "created_at": link.created_at,
        "expires_at": link.expires_at,
        "is_active": link.is_active,
        "last_accessed_at": link.last_accessed_at,
        "days_until_expiry": None
    }
    
    if link.expires_at:
        days_left = (link.expires_at - datetime.utcnow()).days
        stats_dict["days_until_expiry"] = max(0, days_left)
    
    return stats_dict

@router.put("/{short_code}", response_model=LinkResponse)
def update_link(
    short_code: str,
    link_update: LinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    link = LinkService.get_link_stats(db, short_code)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    try:
        updated_link = LinkService.update_link(db, link, link_update, current_user.id)
        response_dict = {
            "id": updated_link.id,
            "short_code": updated_link.short_code,
            "original_url": updated_link.original_url,
            "short_url": f"{settings.BASE_URL}/{updated_link.short_code}",
            "custom_alias": updated_link.custom_alias,
            "clicks": updated_link.clicks,
            "created_at": updated_link.created_at,
            "expires_at": updated_link.expires_at,
            "is_active": updated_link.is_active
        }
        return LinkResponse.model_validate(response_dict)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    link = LinkService.get_link_stats(db, short_code)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    try:
        LinkService.delete_link(db, link, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    db: Session = Depends(get_db)
):
    link = LinkService.get_link(db, short_code)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found or expired"
        )
    
    LinkService.record_click(db, link)
    
    return RedirectResponse(url=link.original_url)