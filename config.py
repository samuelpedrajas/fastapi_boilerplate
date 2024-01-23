import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ACCOUNT_ACTIVATION_TIMEOUT: int = 86400  # 24 hours
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    SERVER_URL: str
    SECRET_KEY: str
    FASTAPI_RUN_PORT: int
    FASTAPI_ENV: str

    POSTGRES_HOST: str
    POSTGRES_PORT: str
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

    CORS_ORIGINS: str
    REDIS_HOST: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_ENDPOINT_URL: str
    AWS_BUCKET_NAME: str
    AWS_REGION: str


class DevelopmentConfig(CommonSettings):
    DEBUG: bool = True
    LOG_FILE: str = "storage/logs/development.log"
    UPLOADS_DIR: str = "storage/uploads"

    @property
    def sqlalchemy_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class ProductionConfig(CommonSettings):
    DEBUG: bool = False
    LOG_FILE: str = "storage/logs/production.log"
    UPLOADS_DIR: str = "storage/uploads"

    @property
    def sqlalchemy_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class TestingConfig(CommonSettings):
    TESTING: bool = True
    DEBUG: bool = True
    LOG_FILE: str = "tests/storage/logs/testing.log"
    UPLOADS_DIR: str = "tests/storage/uploads"

    POSTGRES_TEST_HOST: str
    POSTGRES_TEST_PORT: str
    POSTGRES_TEST_USER: str
    POSTGRES_TEST_PASSWORD: str
    POSTGRES_TEST_DB: str

    @property
    def sqlalchemy_test_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_TEST_USER}:{self.POSTGRES_TEST_PASSWORD}@{self.POSTGRES_TEST_HOST}:{self.POSTGRES_TEST_PORT}/{self.POSTGRES_TEST_DB}"


def get_settings(env) -> BaseSettings:
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    return DevelopmentConfig()


current_env = os.environ.get("FASTAPI_ENV", "testing")
settings = get_settings(current_env)
