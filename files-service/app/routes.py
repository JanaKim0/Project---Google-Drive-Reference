from datetime import datetime, timezone
from typing import Annotated

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pymongo.errors import DuplicateKeyError

from app.auth import get_current_user
from app.db import items_collection
from app.schemas import CreateFolderRequest, FolderResponse, ItemResponse, PathItem

router = APIRouter()

ROOT_FOLDER = "root"
MAX_ITEMS_PER_FOLDER = 1000

FOLDER_NOT_FOUND_MESSAGE = "Folder nije pronađen."
FOLDER_EXISTS_MESSAGE = "Folder sa ovim nazivom već postoji na ovoj lokaciji."

FolderId = Annotated[str, Path(max_length=24)]


def _find_own_folder(folder_id: str, owner_id: str) -> dict:
    try:
        object_id = ObjectId(folder_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FOLDER_NOT_FOUND_MESSAGE)

    folder = items_collection.find_one(
        {"_id": object_id, "owner_id": owner_id, "type": "folder"},
        {"_id": 1, "name": 1, "ancestors": 1},
    )
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FOLDER_NOT_FOUND_MESSAGE)
    return folder


@router.post("/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
def create_folder(data: CreateFolderRequest, user: dict = Depends(get_current_user)):
    owner_id = user["id"]
    parent_id = None
    ancestors = []
    if data.parent_id is not None:
        parent = _find_own_folder(data.parent_id, owner_id)
        parent_id = parent["_id"]
        ancestors = parent.get("ancestors", []) + [parent_id]

    now = datetime.now(timezone.utc)
    folder = {
        "name": data.name,
        "type": "folder",
        "owner_id": owner_id,
        "parent_id": parent_id,
        "ancestors": ancestors,
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


@router.get("/folders/{folder_id}/content", response_model=list[ItemResponse])
def get_folder_content(folder_id: FolderId, user: dict = Depends(get_current_user)):
    owner_id = user["id"]
    parent_id = None
    if folder_id != ROOT_FOLDER:
        parent_id = _find_own_folder(folder_id, owner_id)["_id"]

    items = (
        items_collection.find(
            {"owner_id": owner_id, "parent_id": parent_id},
            {"name": 1, "type": 1, "created_at": 1},
        )
        .sort([("type", -1), ("name", 1)])
        .limit(MAX_ITEMS_PER_FOLDER)
    )

    return [
        ItemResponse(id=str(item["_id"]), name=item["name"], type=item["type"], created_at=item["created_at"])
        for item in items
    ]


@router.get("/folders/{folder_id}/path", response_model=list[PathItem])
def get_folder_path(folder_id: FolderId, user: dict = Depends(get_current_user)):
    if folder_id == ROOT_FOLDER:
        return []

    owner_id = user["id"]
    folder = _find_own_folder(folder_id, owner_id)
    ancestor_ids = folder.get("ancestors", [])

    names = {
        ancestor["_id"]: ancestor["name"]
        for ancestor in items_collection.find(
            {"_id": {"$in": ancestor_ids}, "owner_id": owner_id},
            {"name": 1},
        )
    }

    path = [PathItem(id=str(a_id), name=names[a_id]) for a_id in ancestor_ids if a_id in names]
    path.append(PathItem(id=str(folder["_id"]), name=folder["name"]))
    return path