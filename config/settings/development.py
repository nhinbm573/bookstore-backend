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

CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
CORS_ALLOW_CREDENTIALS = True

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@yourdomain.com")
