from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR_PATH = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR_PATH / ".env"


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DBSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(
        **CustomBaseSettings.model_config,
        env_prefix="DB_",
    )

    host: str
    port: int
    username: str
    password: SecretStr
    name: str

    @computed_field
    @property
    def url(self) -> str:
        postgres_dsn = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.username,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.name,
        )

        return str(postgres_dsn)


class RedisSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(
        **CustomBaseSettings.model_config,
        env_prefix="REDIS_",
    )

    host: str
    port: int
    password: SecretStr
    db_index: int

    @computed_field
    @property
    def url(self) -> str:
        redis_dsn = RedisDsn.build(
            scheme="redis",
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=str(self.db_index),
        )

        return str(redis_dsn)


class CORSSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(
        **CustomBaseSettings.model_config,
        env_prefix="CORS_",
    )

    origins: list[str]


class AuthSettings(CustomBaseSettings):
    model_config = SettingsConfigDict(
        **CustomBaseSettings.model_config,
        env_prefix="AUTH_",
    )

    jwt_secret_key: SecretStr
    access_token_expire_seconds: int
    refresh_token_expire_seconds: int
    refresh_token_pepper: SecretStr
    password_pepper: SecretStr


class Settings(CustomBaseSettings):
    db: DBSettings = Field(default_factory=DBSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)


settings = Settings()
