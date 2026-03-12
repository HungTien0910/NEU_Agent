from pydantic import BaseModel


class SettingsResponse(BaseModel):
    language: str
    timezone: str
    date_format: str
    email_notifications: bool
    error_notifications: bool
    password_rotation_days: int
    mfa_enabled: bool


class SettingsUpdate(BaseModel):
    language: str
    timezone: str
    date_format: str
    email_notifications: bool
    error_notifications: bool
    password_rotation_days: int
    mfa_enabled: bool
