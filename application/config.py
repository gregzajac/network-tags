import os
from pathlib import Path


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    MEMCACHED_SERVER = os.environ.get("MEMCACHED_SERVER")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT"))
    DB_JSON_PATH = Path(os.environ.get("DB_JSON_PATH")).resolve()

    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    hostname = os.environ.get("POSTGRES_HOSTNAME")
    port = os.environ.get("POSTGRES_PORT")
    database = os.environ.get("APPLICATION_DB")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{user}:{password}@{hostname}:{port}/{database}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_FILE_PATH = Path(os.environ.get("LOG_FILE_PATH")).resolve()
    LOG_BACKUP_COUNT = int(os.environ.get("LOG_BACKUP_COUNT"))
    LOG_MAX_BYTES = int(os.environ.get("LOG_MAX_BYTES"))
    LOG_LEVEL = os.environ.get("LOG_LEVEL")


class ProductionConfig(Config):
    """Production configuration"""


class DevelopmentConfig(Config):
    """Development configuration"""


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    ENDPOINT_CASES_PATH = Path(os.environ.get("ENDPOINT_CASES_PATH")).resolve()
