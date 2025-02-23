import os
from dotenv import load_dotenv, find_dotenv


dotenv_path = find_dotenv()
load_dotenv(dotenv_path, override=True)


class Config:
    VERSION = "1.0"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 15,
        "max_overflow": 10,
        "pool_timeout": 30,
    }

    API_HOST = os.getenv("API_HOST")
    API_PORT = os.getenv("API_PORT")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
    UPLOAD_FOLDER = os.path.abspath("uploads/")


class Redis:
    URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


class Twilio:
    ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    PHONE = os.getenv("TWILIO_PHONE")