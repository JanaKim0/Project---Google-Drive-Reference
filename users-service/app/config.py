import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]
VERIFICATION_TOKEN_EXPIRE_MINUTES = int(os.environ["VERIFICATION_TOKEN_EXPIRE_MINUTES"])
OTP_EXPIRE_MINUTES = int(os.environ["OTP_EXPIRE_MINUTES"])
OTP_MAX_ATTEMPTS = int(os.environ["OTP_MAX_ATTEMPTS"])

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
JWT_EXPIRE_MINUTES = int(os.environ["JWT_EXPIRE_MINUTES"])

SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_FROM = os.environ["SMTP_FROM"]
FRONTEND_URL = os.environ["FRONTEND_URL"]

DEFAULT_STORAGE_QUOTA_BYTES = int(os.environ["DEFAULT_STORAGE_QUOTA_BYTES"])