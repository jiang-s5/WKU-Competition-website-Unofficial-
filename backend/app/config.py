import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    INSTANCE_DIR = BASE_DIR / "instance"
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    SECRET_KEY = os.environ.get("WKU_SECRET_KEY", "change-me-in-production")
    DATABASE = os.environ.get("WKU_DATABASE_PATH", str(INSTANCE_DIR / "wku_platform.db"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("WKU_COOKIE_SECURE", "0") == "1"
    DEMO_SMS = os.environ.get("WKU_DEMO_SMS", "1") == "1"
    SMS_PROVIDER = os.environ.get("WKU_SMS_PROVIDER", "demo")
    SMS_ACCESS_KEY_ID = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", os.environ.get("WKU_SMS_ACCESS_KEY_ID", ""))
    SMS_ACCESS_KEY_SECRET = os.environ.get(
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
        os.environ.get("WKU_SMS_ACCESS_KEY_SECRET", ""),
    )
    SMS_ENDPOINT = os.environ.get("WKU_SMS_ENDPOINT", "dysmsapi.aliyuncs.com")
    SMS_SIGN_NAME = os.environ.get("WKU_SMS_SIGN_NAME", "")
    SMS_TEMPLATE_PARAM_KEY = os.environ.get("WKU_SMS_TEMPLATE_PARAM_KEY", "code")
    SMS_TEMPLATE_CODE_REGISTER = os.environ.get("WKU_SMS_TEMPLATE_CODE_REGISTER", "")
    SMS_TEMPLATE_CODE_RESET = os.environ.get("WKU_SMS_TEMPLATE_CODE_RESET", "")
    SMS_RESEND_SECONDS = int(os.environ.get("WKU_SMS_RESEND_SECONDS", "60"))
    SMS_EXPIRE_MINUTES = int(os.environ.get("WKU_SMS_EXPIRE_MINUTES", "10"))
