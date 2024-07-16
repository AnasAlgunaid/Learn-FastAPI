from datetime import date
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CreateUser(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    phone: str


class ReadUser(BaseModel):
    user_id: int
    name: str
    username: str
    email: EmailStr
    phone: str
    is_verified: bool
    created_at: datetime


class UpdateUser(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
