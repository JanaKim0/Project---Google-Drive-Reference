import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]