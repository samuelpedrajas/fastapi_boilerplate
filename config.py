import os
from pydantic_settings import BaseSettings

class CommonSettings(BaseSettings):
    ACCOUNT_ACTIVATION_TIMEOUT: int = 86400  # 24 hours
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    SERVER_NAME: str
    SECRET_KEY: str
    FASTAPI_RUN_PORT: int
    FASTAPI_ENV: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_USE_TLS: bool
    MAIL_USE_SSL: bool
    MAIL_FROM_EMAIL: str

    @property
    def sqlalchemy_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"


class DevelopmentConfig(CommonSettings):
    DEBUG: bool = True
    LOG_FILE: str = "storage/logs/development.log"
    UPLOADS_DIR: str = "storage/uploads"


class ProductionConfig(CommonSettings):
    DEBUG: bool = False
    LOG_FILE: str = "storage/logs/production.log"
    UPLOADS_DIR: str = "storage/uploads"


class TestingConfig(CommonSettings):
    TESTING: bool = True
    DEBUG: bool = True
    LOG_FILE: str = "tests/storage/logs/testing.log"
    UPLOADS_DIR: str = "tests/storage/uploads"

    POSTGRES_TEST_USER: str
    POSTGRES_TEST_PASSWORD: str
    POSTGRES_TEST_DB: str

    @property
    def sqlalchemy_database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_TEST_USER}:{self.POSTGRES_TEST_PASSWORD}@db/{self.POSTGRES_TEST_DB}"


def get_settings() -> BaseSettings:
    env = os.environ.get("FASTAPI_ENV", "development")
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    return DevelopmentConfig()


settings = get_settings()
