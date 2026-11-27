import re

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

NAME_REGEX = re.compile(r"^[A-Za-zČĆŽŠĐčćžšđ' -]{2,50}$")
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
OTP_REGEX = re.compile(r"[0-9]{6}")

EMAIL_MAX_LENGTH = 254
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64
BCRYPT_MAX_BYTES = 72

NAME_LABELS = {"first_name": "Ime", "last_name": "Prezime"}


def validate_email_value(value: str) -> str:
    value = value.strip().lower()
    if not value:
        raise ValueError("Imejl je obavezan.")
    if len(value) > EMAIL_MAX_LENGTH or not EMAIL_REGEX.fullmatch(value):
        raise ValueError("Imejl nije u ispravnom formatu.")
    return value


def validate_password_input(value: str) -> str:
    if not value:
        raise ValueError("Lozinka je obavezna.")
    if len(value) > PASSWORD_MAX_LENGTH or len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError("Lozinka je predugačka.")
    return value


def validate_password_strength(value: str) -> str:
    if not value:
        raise ValueError("Lozinka je obavezna.")
    if not PASSWORD_MIN_LENGTH <= len(value) <= PASSWORD_MAX_LENGTH:
        raise ValueError("Lozinka mora imati između 8 i 64 karaktera.")
    if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError("Lozinka je predugačka.")
    if not (
        re.search(r"[A-Z]", value)
        and re.search(r"[a-z]", value)
        and re.search(r"[0-9]", value)
        and re.search(r"[^A-Za-z0-9]", value)
    ):
        raise ValueError(
            "Lozinka mora sadržati veliko slovo, malo slovo, cifru i specijalni karakter."
        )
    return value


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str, info: ValidationInfo) -> str:
        label = NAME_LABELS[info.field_name]
        value = value.strip()
        if not value:
            raise ValueError(f"{label} je obavezno.")
        if not NAME_REGEX.fullmatch(value):
            raise ValueError(f"{label} može sadržati samo slova (2–50 karaktera).")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email_value(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_strength(value)

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, value: str, info: ValidationInfo) -> str:
        password = info.data.get("password")
        if password is not None and value != password:
            raise ValueError("Lozinke se ne poklapaju.")
        return value


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email_value(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_password_input(value)


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("current_password")
    @classmethod
    def validate_current_password(cls, value: str) -> str:
        return validate_password_input(value)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str, info: ValidationInfo) -> str:
        value = validate_password_strength(value)
        if value == info.data.get("current_password"):
            raise ValueError("Nova lozinka mora biti različita od trenutne.")
        return value

    @field_validator("confirm_new_password")
    @classmethod
    def validate_confirm_new_password(cls, value: str, info: ValidationInfo) -> str:
        new_password = info.data.get("new_password")
        if new_password is not None and value != new_password:
            raise ValueError("Lozinke se ne poklapaju.")
        return value


class VerifyOtpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    otp: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email_value(value)

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        value = value.strip()
        if not OTP_REGEX.fullmatch(value):
            raise ValueError("Kod mora imati tačno 6 cifara.")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class VerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1, max_length=128)


class MessageResponse(BaseModel):
    message: str


class QuotaResponse(BaseModel):
    quota_bytes: int
    used_bytes: int
    available_bytes: int