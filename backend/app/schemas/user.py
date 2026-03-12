from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=1)
    full_name: str = Field(..., min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    department: Optional[str] = None
    role: str = "user"
    permissions: List[str] = []
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserListItem(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    title: Optional[str]
    role: str
    is_active: bool


class UserDetail(UserBase):
    id: int


class UserListResponse(BaseModel):
    items: List[UserListItem]
    total: int
    limit: int
    skip: int
