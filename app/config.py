from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 5001
    MAX_IN_FLIGHT: int = 50
    PER_USER_MAX: int = 2
    RATE_WINDOW_SECONDS: int = 10
    RATE_MAX_MESSAGES: int = 6

    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    MODEL_NAME: str | None = None
    # LLM / provider configuration (from .env)
    LLM_URL: str | None = "https://api.groq.com/openai/v1/chat/completions"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 200

    class Config:
        env_file = ".env"

settings = Settings()
