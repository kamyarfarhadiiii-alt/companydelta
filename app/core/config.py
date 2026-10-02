from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "شرکت دلتا"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    database_url: str = "sqlite:///./app.db"
    cookie_secure: bool = False  # در Production با HTTPS برابر true شود

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
