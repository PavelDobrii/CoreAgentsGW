from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .profile import ProfileResponse


class LoginData(BaseModel):
    email: EmailStr
    password: str


class RegisterData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    password: str
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    phone_number: str | None = Field(default=None, alias="phoneNumber")
    country: str | None = None
    city: str | None = None


class RefreshRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    refresh_token: str = Field(alias="refreshToken")


class Tokens(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str
    refresh_token: str


class AuthResponse(Tokens):
    user: ProfileResponse
