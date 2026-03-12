from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.services.auth_service import (
    authenticate,
    build_login_response,
    request_password_reset,
    reset_password,
    send_reset_email,
)
from app.repositories.user_repo import clear_reset_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user, status_code = authenticate(db, payload.username, payload.password)

    if status_code == "invalid_credentials":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng.",
        )

    if status_code == "inactive":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đang bị khóa.",
        )

    return build_login_response(user)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user, token = request_password_reset(db, payload.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản.",
        )
    if not user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa có email để nhận liên kết đặt lại.",
        )

    base_url = settings.frontend_base_url or request.headers.get("origin") or ""
    if not base_url:
        clear_reset_token(db, user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Thiếu cấu hình FRONTEND_BASE_URL hoặc Origin để gửi email.",
        )

    reset_link = f"{base_url.rstrip('/')}/reset-password?token={token}"
    try:
        send_reset_email(user.email, reset_link)
    except RuntimeError as exc:
        clear_reset_token(db, user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception:
        clear_reset_token(db, user)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể gửi email đặt lại mật khẩu. Vui lòng kiểm tra SMTP.",
        )

    return {"message": "Đã gửi liên kết đặt lại mật khẩu qua email."}


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password_endpoint(
    payload: ResetPasswordRequest, db: Session = Depends(get_db)
):
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu xác nhận không khớp.",
        )

    _, status_code = reset_password(db, payload.token, payload.new_password)
    if status_code == "invalid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Liên kết đặt lại không hợp lệ.",
        )

    if status_code == "expired":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Liên kết đặt lại đã hết hạn.",
        )

    return {"message": "Đặt lại mật khẩu thành công."}
