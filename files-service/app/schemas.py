import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

NAME_MAX_LENGTH = 255
FORBIDDEN_NAME_CHARS = re.compile(r"[/\\\x00-\x1f]")


class CreateFolderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    parent_id: str | None = Field(default=None, max_length=24)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Naziv foldera je obavezan.")
        if len(value) > NAME_MAX_LENGTH:
            raise ValueError("Naziv foldera može imati najviše 255 karaktera.")
        if FORBIDDEN_NAME_CHARS.search(value):
            raise ValueError("Naziv foldera ne sme sadržati znakove / i \\.")
        if set(value) == {"."}:
            raise ValueError("Naziv foldera nije dozvoljen.")
        return value


class FolderResponse(BaseModel):
    id: str
    name: str
    parent_id: str | None
    created_at: datetime


class ItemResponse(BaseModel):
    id: str
    name: str
    type: str
    created_at: datetime


class PathItem(BaseModel):
    id: str
    name: str