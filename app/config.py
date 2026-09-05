from pydantic_settings import BaseSettings, SettingsConfigDict
 
 
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
 
    api_key: str = "dev-secret-key"
    transaction_service_url: str = "http://localhost:8001"
 
 
settings = Settings()