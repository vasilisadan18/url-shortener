from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from datetime import datetime
from typing import Optional

class LinkBase(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(None, min_length=3, max_length=20)
    expires_at: Optional[datetime] = None

class LinkCreate(LinkBase):
    pass

class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    custom_alias: Optional[str]= None
    expires_at: Optional[datetime] = None

class LinkResponse(BaseModel):
    id: str
    short_code: str
    original_url: str
    short_url: str
    custom_alias: Optional[str] = None
    clicks: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class LinkStats(LinkResponse):
    last_accessed_at: Optional[datetime]=None
    days_until_expiry: Optional[int]=None

class LinkSearchResult(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    clicks: int
    
    model_config = ConfigDict(from_attributes=True)