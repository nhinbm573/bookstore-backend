from .base import *
from decouple import config

SECRET_KEY = config("SECRET_KEY", default="your-secret-key")

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,0.0.0.0",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="your_project_dev"),
        "USER": config("DB_USER", default="your_db_user"),
        "PASSWORD": config("DB_PASSWORD", default="your_db_password"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
