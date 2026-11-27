import logging
import smtplib
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.auth import NOT_AUTHENTICATED_MESSAGE, get_current_token
from app.config import (
    DEFAULT_STORAGE_QUOTA_BYTES,
    JWT_EXPIRE_MINUTES,
    OTP_EXPIRE_MINUTES,
    OTP_MAX_ATTEMPTS,
    PASSWORD_MIN_AGE_MINUTES,
    PASSWORD_RESET_EXPIRE_MINUTES,
    VERIFICATION_TOKEN_EXPIRE_MINUTES,
)
from app.db import audit_log_collection, revoked_tokens_collection, users_collection
from app.email_service import send_otp_email, send_password_reset_email, send_verification_email
from app.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    QuotaResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    VerifyOtpRequest,
    VerifyRequest,
)
from app.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    generate_otp,
    generate_token,
    hash_otp,
    hash_password,
    hash_token,
    is_password_expired,
    verify_otp,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter()

EMAIL_TAKEN_MESSAGE = "Imejl je već registrovan."
INVALID_TOKEN_MESSAGE = "Link za potvrdu nije ispravan ili je već iskorišćen."
EXPIRED_TOKEN_MESSAGE = "Link za potvrdu je istekao."
INVALID_USER_ID_MESSAGE = "Neispravan identifikator korisnika."
USER_NOT_FOUND_MESSAGE = "Korisnik nije pronađen."
INVALID_CREDENTIALS_MESSAGE = "Pogrešan imejl ili lozinka."
ACCOUNT_NOT_VERIFIED_MESSAGE = "Nalog nije potvrđen. Proverite svoj imejl."
OTP_SEND_FAILED_MESSAGE = "Slanje koda nije uspelo. Pokušajte ponovo."
INVALID_OTP_MESSAGE = "Kod nije ispravan ili je istekao. Prijavite se ponovo."
WRONG_OTP_MESSAGE = "Kod nije ispravan. Preostalo pokušaja: {remaining}."
TOO_MANY_ATTEMPTS_MESSAGE = "Previše pogrešnih pokušaja. Prijavite se ponovo."
LOGOUT_SUCCESS_MESSAGE = "Uspešno ste se odjavili."
WRONG_CURRENT_PASSWORD_MESSAGE = "Trenutna lozinka nije ispravna."
PASSWORD_TOO_NEW_MESSAGE = "Lozinka mora biti stara najmanje jedan dan da bi se mogla promeniti."
PASSWORD_CHANGED_MESSAGE = "Lozinka je uspešno promenjena. Prijavite se ponovo."
PASSWORD_RESET_REQUESTED_MESSAGE = "Ako nalog sa ovim imejlom postoji, poslali smo link za resetovanje lozinke."
INVALID_RESET_TOKEN_MESSAGE = "Link za resetovanje lozinke nije ispravan ili je već iskorišćen."
EXPIRED_RESET_TOKEN_MESSAGE = "Link za resetovanje lozinke je istekao. Zatražite novi."
SAME_PASSWORD_MESSAGE = "Nova lozinka mora biti različita od trenutne."
PASSWORD_RESET_SUCCESS_MESSAGE = "Lozinka je uspešno resetovana. Prijavite se sa novom lozinkom."
PASSWORD_EXPIRED_MESSAGE = (
    "Vaša lozinka je istekla i prijava je privremeno onemogućena. "
    "Postavite novu lozinku putem opcije „Zaboravili ste lozinku?“."
)
PASSWORD_EXPIRED_CODE = "PASSWORD_EXPIRED"

PASSWORD_RESET_COOLDOWN = timedelta(minutes=1)

OTP_FIELDS = {"otp_hash": "", "otp_expires_at": "", "otp_attempts": ""}
PASSWORD_RESET_FIELDS = {"password_reset_token_hash": "", "password_reset_expires_at": ""}


def _log_security_event(user_id, event: str) -> None:
    audit_log_collection.insert_one(
        {"user_id": str(user_id), "event": event, "created_at": datetime.now(timezone.utc)}
    )


def _lock_expired_account(user) -> None:
    result = users_collection.update_one(
        {"_id": user["_id"], "password_expired_locked_at": {"$exists": False}},
        {"$set": {"password_expired_locked_at": datetime.now(timezone.utc)}},
    )
    if result.modified_count:
        _log_security_event(user["_id"], "ACCOUNT_LOCKED_PASSWORD_EXPIRED")
    logger.warning("Odbijena prijava zbog istekle lozinke za korisnika %s", user["_id"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    if users_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN_MESSAGE)

    now = datetime.now(timezone.utc)
    verification_token = generate_token()

    user = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "role": "user",
        "is_verified": False,
        "created_at": now,
        "password_changed_at": now,
        "verification_token_hash": hash_token(verification_token),
        "verification_token_expires_at": now + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES),
        "storage_quota_bytes": DEFAULT_STORAGE_QUOTA_BYTES,
        "storage_used_bytes": 0,
    }

    try:
        result = users_collection.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_TAKEN_MESSAGE)

    try:
        send_verification_email(data.email, data.first_name, verification_token)
    except (smtplib.SMTPException, OSError):
        logger.warning("Slanje imejla za potvrdu nije uspelo za korisnika %s", result.inserted_id)

    return UserResponse(
        id=str(result.inserted_id),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
    )


@router.post("/verify", response_model=MessageResponse)
def verify_account(data: VerifyRequest):
    user = users_collection.find_one({"verification_token_hash": hash_token(data.token)})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_TOKEN_MESSAGE)

    if user["verification_token_expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EXPIRED_TOKEN_MESSAGE)

    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"is_verified": True},
            "$unset": {"verification_token_hash": "", "verification_token_expires_at": ""},
        },
    )

    return MessageResponse(message="Nalog je uspešno potvrđen.")


@router.post("/login", response_model=MessageResponse)
def login(data: LoginRequest):
    user = users_collection.find_one({"email": data.email})
    password_hash = user["password_hash"] if user else DUMMY_PASSWORD_HASH
    password_valid = verify_password(data.password, password_hash)

    if not user or not password_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS_MESSAGE)

    if not user.get("is_verified"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ACCOUNT_NOT_VERIFIED_MESSAGE)

    if is_password_expired(user.get("password_changed_at")):
        _lock_expired_account(user)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": PASSWORD_EXPIRED_MESSAGE, "code": PASSWORD_EXPIRED_CODE},
        )

    otp = generate_otp()
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "otp_hash": hash_otp(otp),
                "otp_expires_at": datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES),
                "otp_attempts": 0,
            }
        },
    )

    try:
        send_otp_email(user["email"], user["first_name"], otp)
    except (smtplib.SMTPException, OSError):
        logger.warning("Slanje OTP koda nije uspelo za korisnika %s", user["_id"])
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=OTP_SEND_FAILED_MESSAGE)

    return MessageResponse(message="Kod za prijavu je poslat na imejl.")


def _clear_otp(user_id) -> None:
    users_collection.update_one({"_id": user_id}, {"$unset": OTP_FIELDS})


@router.post("/login/verify", response_model=TokenResponse)
def verify_login_otp(data: VerifyOtpRequest):
    user = users_collection.find_one_and_update(
        {"email": data.email, "otp_hash": {"$exists": True}},
        {"$inc": {"otp_attempts": 1}},
        return_document=ReturnDocument.AFTER,
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_OTP_MESSAGE)

    if user["otp_attempts"] > OTP_MAX_ATTEMPTS:
        _clear_otp(user["_id"])
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=TOO_MANY_ATTEMPTS_MESSAGE)

    if user["otp_expires_at"] < datetime.now(timezone.utc):
        _clear_otp(user["_id"])
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_OTP_MESSAGE)

    if not verify_otp(data.otp, user["otp_hash"]):
        remaining = OTP_MAX_ATTEMPTS - user["otp_attempts"]
        if remaining <= 0:
            _clear_otp(user["_id"])
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=TOO_MANY_ATTEMPTS_MESSAGE)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=WRONG_OTP_MESSAGE.format(remaining=remaining),
        )

    result = users_collection.update_one(
        {"_id": user["_id"], "otp_hash": user["otp_hash"]},
        {"$unset": OTP_FIELDS},
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_OTP_MESSAGE)

    access_token = create_access_token(str(user["_id"]), user.get("role", "user"))
    return TokenResponse(access_token=access_token, expires_in=JWT_EXPIRE_MINUTES * 60)


@router.post("/logout", response_model=MessageResponse)
def logout(token: dict = Depends(get_current_token)):
    try:
        revoked_tokens_collection.insert_one(
            {
                "jti": token["jti"],
                "user_id": token["sub"],
                "expires_at": datetime.fromtimestamp(token["exp"], tz=timezone.utc),
                "revoked_at": datetime.now(timezone.utc),
            }
        )
    except DuplicateKeyError:
        pass

    return MessageResponse(message=LOGOUT_SUCCESS_MESSAGE)


@router.post("/users/me/password", response_model=MessageResponse)
def change_password(data: ChangePasswordRequest, token: dict = Depends(get_current_token)):
    user = users_collection.find_one({"_id": ObjectId(token["sub"])})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_AUTHENTICATED_MESSAGE)

    if not verify_password(data.current_password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=WRONG_CURRENT_PASSWORD_MESSAGE)

    now = datetime.now(timezone.utc)
    password_changed_at = user.get("password_changed_at")
    if password_changed_at and now - password_changed_at < timedelta(minutes=PASSWORD_MIN_AGE_MINUTES):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_TOO_NEW_MESSAGE)

    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password_hash": hash_password(data.new_password), "password_changed_at": now},
            "$unset": {"password_expired_locked_at": ""},
        },
    )

    return MessageResponse(message=PASSWORD_CHANGED_MESSAGE)


def _send_password_reset_email_safely(user_id, email: str, first_name: str, token: str) -> None:
    try:
        send_password_reset_email(email, first_name, token)
    except (smtplib.SMTPException, OSError):
        logger.warning("Slanje linka za resetovanje lozinke nije uspelo za korisnika %s", user_id)


@router.post("/password-reset/request", response_model=MessageResponse)
def request_password_reset(data: PasswordResetRequest, background_tasks: BackgroundTasks):
    now = datetime.now(timezone.utc)
    token = generate_token()

    user = users_collection.find_one_and_update(
        {
            "email": data.email,
            "is_verified": True,
            "$or": [
                {"password_reset_requested_at": {"$exists": False}},
                {"password_reset_requested_at": {"$lt": now - PASSWORD_RESET_COOLDOWN}},
            ],
        },
        {
            "$set": {
                "password_reset_token_hash": hash_token(token),
                "password_reset_expires_at": now + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES),
                "password_reset_requested_at": now,
            }
        },
        projection={"email": 1, "first_name": 1},
    )

    if user:
        background_tasks.add_task(
            _send_password_reset_email_safely, user["_id"], user["email"], user["first_name"], token
        )

    return MessageResponse(message=PASSWORD_RESET_REQUESTED_MESSAGE)


@router.post("/password-reset/confirm", response_model=MessageResponse)
def confirm_password_reset(data: PasswordResetConfirmRequest):
    token_hash = hash_token(data.token)
    user = users_collection.find_one({"password_reset_token_hash": token_hash})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_RESET_TOKEN_MESSAGE)

    now = datetime.now(timezone.utc)
    if user["password_reset_expires_at"] < now:
        users_collection.update_one({"_id": user["_id"]}, {"$unset": PASSWORD_RESET_FIELDS})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EXPIRED_RESET_TOKEN_MESSAGE)

    password_changed_at = user.get("password_changed_at")
    if password_changed_at and now - password_changed_at < timedelta(minutes=PASSWORD_MIN_AGE_MINUTES):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_TOO_NEW_MESSAGE)

    if verify_password(data.new_password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=SAME_PASSWORD_MESSAGE)

    result = users_collection.update_one(
        {"_id": user["_id"], "password_reset_token_hash": token_hash},
        {
            "$set": {"password_hash": hash_password(data.new_password), "password_changed_at": now},
            "$unset": {**PASSWORD_RESET_FIELDS, "password_expired_locked_at": ""},
        },
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_RESET_TOKEN_MESSAGE)

    if user.get("password_expired_locked_at"):
        _log_security_event(user["_id"], "ACCOUNT_UNLOCKED_PASSWORD_RESET")

    return MessageResponse(message=PASSWORD_RESET_SUCCESS_MESSAGE)


@router.get("/users/{user_id}/quota", response_model=QuotaResponse)
def get_user_quota(user_id: str):
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_USER_ID_MESSAGE)

    user = users_collection.find_one(
        {"_id": object_id},
        {"storage_quota_bytes": 1, "storage_used_bytes": 1},
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND_MESSAGE)

    quota = user.get("storage_quota_bytes", 0)
    used = user.get("storage_used_bytes", 0)

    return QuotaResponse(
        quota_bytes=quota,
        used_bytes=used,
        available_bytes=max(quota - used, 0),
    )