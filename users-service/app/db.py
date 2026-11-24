import logging

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import MONGO_URI, MONGO_DB_NAME

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, tz_aware=True)
db = client[MONGO_DB_NAME]
users_collection = db["users"]


def ensure_indexes():
    try:
        users_collection.create_index("email", unique=True)
    except PyMongoError as e:
        logger.warning("Nije moguće kreirati indeks za imejl: %s", e)