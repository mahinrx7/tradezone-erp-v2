import os

from dotenv import load_dotenv

load_dotenv()

class Config:

    SECRET_KEY = "tradezone_secret_key"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///tradezone.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False