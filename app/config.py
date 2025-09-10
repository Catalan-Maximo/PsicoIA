from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_HOST: str | None = None
    APP_PORT: int | None = None
    MAX_IN_FLIGHT: int | None = None
    PER_USER_MAX: int | None = None
    RATE_WINDOW_SECONDS: int | None = None
    RATE_MAX_MESSAGES: int | None = None

    #GROQ_API_KEY se puede cambiar por otro proveedor de APIs
    GROQ_API_KEY: str | None = None
    MODEL_NAME: str | None = None
    LLM_URL: str | None = None

    #Configuración del LLM
    LLM_TEMPERATURE: float | None = None
    LLM_MAX_TOKENS: int | None = None
    LLM_TIMEOUT_SECONDS: float | None = None
    LLM_MAX_RETRIES: int | None = None
    LLM_BACKOFF_INITIAL: float | None = None
    LLM_BACKOFF_MAX: float | None = None
    LLM_HISTORY_MAX_MESSAGES: int | None = None
    LLM_INPUT_TOKEN_BUDGET: int | None = None
    LLM_CHARS_PER_TOKEN: int | None = None

    class Config:
        env_file = ".env"

settings = Settings()
