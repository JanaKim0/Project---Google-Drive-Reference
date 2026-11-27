import logging

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import MONGO_URI, MONGO_DB_NAME

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, tz_aware=True)
db = client[MONGO_DB_NAME]
items_collection = db["items"]


def ensure_indexes():
    try:
        items_collection.create_index([("owner_id", 1), ("parent_id", 1)])
        items_collection.create_index(
            [("owner_id", 1), ("parent_id", 1), ("name", 1)],
            unique=True,
            partialFilterExpression={"type": "folder"},
            name="unique_folder_name_per_parent",
        )
    except PyMongoError as e:
        logger.warning("Nije moguće kreirati indekse za stavke: %s", e)