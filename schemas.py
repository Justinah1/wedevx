from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from models import LeadState

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    
class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    state: Optional[LeadState] = None
    notes: Optional[str] = None

class LeadInDB(LeadBase):
    id: int
    resume_path: str
    state: LeadState
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

class Lead(LeadInDB):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
