from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 5001
    MAX_IN_FLIGHT: int = 50
    PER_USER_MAX: int = 2
    RATE_WINDOW_SECONDS: int = 10
    RATE_MAX_MESSAGES: int = 6

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "psicoia"

    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    MODEL_NAME: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
