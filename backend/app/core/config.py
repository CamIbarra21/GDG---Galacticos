from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la app, cargada desde variables de entorno / .env.

    IMPORTANTE: nunca hardcodear API keys aquí. Todo viene de .env
    (que está en .gitignore) o de las variables de entorno del servidor
    donde se haga el deploy.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "tutor_educativo"

    # "local" -> Ollama | "cloud" -> Gemini API sirviendo Gemma 4
    mode: str = "local"

    # Modo local (Ollama)
    ollama_model: str = "gemma4:e2b"
    ollama_api_base: str = "http://localhost:11434"

    # Modo cloud (Gemini API / Google AI Studio)
    google_api_key: str = ""
    gemini_gemma_model: str = "gemma-4-4b-it"

    # Base de datos
    database_url: str = "sqlite:///./app.db"


settings = Settings()
