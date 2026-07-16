from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERPAPI_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""
    META_ACCESS_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
