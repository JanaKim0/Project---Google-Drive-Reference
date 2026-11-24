import re

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

NAME_REGEX = re.compile(r"^[A-Za-zČĆŽŠĐčćžšđ' -]{2,50}$")
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

EMAIL_MAX_LENGTH = 254
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 64
BCRYPT_MAX_BYTES = 72

NAME_LABELS = {"first_name": "Ime", "last_name": "Prezime"}


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
        value = value.strip().lower()
        if not value:
            raise ValueError("Imejl je obavezan.")
        if len(value) > EMAIL_MAX_LENGTH or not EMAIL_REGEX.fullmatch(value):
            raise ValueError("Imejl nije u ispravnom formatu.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
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