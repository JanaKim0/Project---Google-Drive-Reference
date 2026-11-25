import logging

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import MONGO_URI, MONGO_DB_NAME

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, tz_aware=True)
db = client[MONGO_DB_NAME]
users_collection = db["users"]
revoked_tokens_collection = db["revoked_tokens"]


def ensure_indexes():
    try:
        users_collection.create_index("email", unique=True)
    except PyMongoError as e:
        logger.warning("Nije moguće kreirati indeks za imejl: %s", e)

    try:
        revoked_tokens_collection.create_index("jti", unique=True)
        revoked_tokens_collection.create_index("expires_at", expireAfterSeconds=0)
    except PyMongoError as e:
        logger.warning("Nije moguće kreirati indekse za poništene tokene: %s", e)