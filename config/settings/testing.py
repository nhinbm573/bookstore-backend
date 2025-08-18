from .base import *
from decouple import config

SECRET_KEY = "test-key-for-testing-only"

DEBUG = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,0.0.0.0",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("TEST_DB_NAME", default="test_db"),
        "USER": config("TEST_DB_USER", default="test_user"),
        "PASSWORD": config("TEST_DB_PASSWORD", default="test_password"),
        "HOST": config("TEST_DB_HOST", default="localhost"),
        "PORT": config("TEST_DB_PORT", default="5432", cast=int),
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
