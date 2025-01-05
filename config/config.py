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
    API_KEY = os.getenv("API_KEY")
