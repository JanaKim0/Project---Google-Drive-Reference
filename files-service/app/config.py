import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]
USERS_SERVICE_URL = os.environ["USERS_SERVICE_URL"]
USERS_SERVICE_TIMEOUT_SECONDS = float(os.environ["USERS_SERVICE_TIMEOUT_SECONDS"])
FRONTEND_URL = os.environ["FRONTEND_URL"]