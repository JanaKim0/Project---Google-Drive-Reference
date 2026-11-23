from pymongo import MongoClient
from app.config import MONGO_URI, MONGO_DB_NAME

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = client[MONGO_DB_NAME]
users_collection = db["users"]