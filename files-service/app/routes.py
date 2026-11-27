from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.auth import get_current_user
from app.db import items_collection
from app.schemas import CreateFolderRequest, FolderResponse

router = APIRouter()

FOLDER_NOT_FOUND_MESSAGE = "Folder nije pronađen."
FOLDER_EXISTS_MESSAGE = "Folder sa ovim nazivom već postoji na ovoj lokaciji."


def _find_own_folder(folder_id: str, owner_id: str) -> dict:
    try:
        object_id = ObjectId(folder_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FOLDER_NOT_FOUND_MESSAGE)

    folder = items_collection.find_one(
        {"_id": object_id, "owner_id": owner_id, "type": "folder"},
        {"_id": 1},
    )
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FOLDER_NOT_FOUND_MESSAGE)
    return folder


@router.post("/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
def create_folder(data: CreateFolderRequest, user: dict = Depends(get_current_user)):
    owner_id = user["id"]
    parent_id = None
    if data.parent_id is not None:
        parent_id = _find_own_folder(data.parent_id, owner_id)["_id"]

    now = datetime.now(timezone.utc)
    folder = {
        "name": data.name,
        "type": "folder",
        "owner_id": owner_id,
        "parent_id": parent_id,
        "created_at": now,
        "updated_at": now,
    }

    try:
        result = items_collection.insert_one(folder)
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=FOLDER_EXISTS_MESSAGE)

    return FolderResponse(
        id=str(result.inserted_id),
        name=data.name,
        parent_id=str(parent_id) if parent_id else None,
        created_at=now,
    )