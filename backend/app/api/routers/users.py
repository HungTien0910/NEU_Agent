from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repo import (
    create_user,
    get_by_username,
    list_users,
    count_users,
    update_user,
)
from app.repositories.log_repo import create_log
from app.schemas.user import UserCreate, UserDetail, UserListItem, UserListResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

ALLOWED_PERMISSIONS = {
    "data:student",
    "data:course",
    "data:lecturer",
    "data:academic",
}


@router.get("", response_model=UserListResponse)
def get_users(
    search: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
):
    users = list_users(db, search=search, limit=limit, skip=skip)
    total = count_users(db, search=search)
    items = [
        UserListItem(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            title=user.title,
            role=user.role,
            is_active=user.is_active,
        )
        for user in users
    ]
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "skip": skip,
    }


@router.post("", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)):
    existing = get_by_username(db, payload.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tài khoản đã tồn tại."
        )
    permissions = [p for p in (payload.permissions or []) if p in ALLOWED_PERMISSIONS]
    user = create_user(
        db=db,
        username=payload.username,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
        permissions=permissions,
        email=payload.email,
    )
    user.phone = payload.phone
    user.title = payload.title
    user.birth_date = payload.birth_date
    user.gender = payload.gender
    user.address = payload.address
    user.department = payload.department
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    create_log(
        db,
        actor="Admin",
        action="Thêm mới",
        target="Tài khoản",
        detail=f"Tạo tài khoản {user.username} ({user.title or 'Cán bộ'})",
    )
    return UserDetail(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        title=user.title,
        birth_date=user.birth_date,
        gender=user.gender,
        address=user.address,
        department=user.department,
        role=user.role,
        permissions=permissions,
        is_active=user.is_active,
    )


@router.get("/by-username/{username}", response_model=UserDetail)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = get_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    permissions = [p for p in (user.permissions or "").split(",") if p]
    return UserDetail(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        title=user.title,
        birth_date=user.birth_date,
        gender=user.gender,
        address=user.address,
        department=user.department,
        role=user.role,
        permissions=permissions,
        is_active=user.is_active,
    )


@router.get("/{user_id}", response_model=UserDetail)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    permissions = [p for p in (user.permissions or "").split(",") if p]
    return UserDetail(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        title=user.title,
        birth_date=user.birth_date,
        gender=user.gender,
        address=user.address,
        department=user.department,
        role=user.role,
        permissions=permissions,
        is_active=user.is_active,
    )


@router.put("/{user_id}", response_model=UserDetail)
def update_user_endpoint(
    user_id: int, payload: UserUpdate, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    old_permissions = [p for p in (user.permissions or "").split(",") if p]
    old_values = {
        "username": user.username,
        "full_name": user.full_name,
        "title": user.title,
        "birth_date": user.birth_date,
        "gender": user.gender,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "department": user.department,
        "is_active": user.is_active,
        "permissions": old_permissions,
    }

    data = payload.dict(exclude_unset=True)
    if "username" in data and data["username"] != user.username:
        existing = get_by_username(db, data["username"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản đã tồn tại.",
            )
    if "password" in data:
        data["hashed_password"] = hash_password(data.pop("password"))
    if "permissions" in data and data["permissions"] is not None:
        filtered = [p for p in data["permissions"] if p in ALLOWED_PERMISSIONS]
        data["permissions"] = ",".join(filtered)
    update_user(db, user, data)

    changed_fields = []
    field_labels = {
        "username": "Tên tài khoản",
        "full_name": "Họ tên",
        "title": "Chức danh",
        "birth_date": "Ngày sinh",
        "gender": "Giới tính",
        "email": "Email",
        "phone": "SĐT",
        "address": "Địa chỉ",
        "department": "Khoa",
        "is_active": "Trạng thái",
        "permissions": "Phân quyền",
        "password": "Mật khẩu",
    }

    for key in [
        "username",
        "full_name",
        "title",
        "birth_date",
        "gender",
        "email",
        "phone",
        "address",
        "department",
        "is_active",
    ]:
        if key in data and data.get(key) != old_values.get(key):
            changed_fields.append(field_labels[key])

    if "permissions" in payload.dict(exclude_unset=True):
        new_permissions = [p for p in (payload.permissions or []) if p in ALLOWED_PERMISSIONS]
        if sorted(new_permissions) != sorted(old_values["permissions"]):
            changed_fields.append(field_labels["permissions"])

    if "password" in payload.dict(exclude_unset=True):
        changed_fields.append(field_labels["password"])

    detail = f"Cập nhật tài khoản {user.username}"
    if changed_fields:
        detail = f"{detail}: {', '.join(changed_fields)}"

    create_log(
        db,
        actor="Admin",
        action="Chỉnh sửa",
        target="Tài khoản",
        detail=detail,
    )

    permissions = [p for p in (user.permissions or "").split(",") if p]
    return UserDetail(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        title=user.title,
        birth_date=user.birth_date,
        gender=user.gender,
        address=user.address,
        department=user.department,
        role=user.role,
        permissions=permissions,
        is_active=user.is_active,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    db.delete(user)
    db.commit()
    create_log(
        db,
        actor="Admin",
        action="Xóa",
        target="Tài khoản",
        detail=f"Xóa tài khoản {user.username}",
    )
