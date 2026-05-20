import os
from dotenv import load_dotenv

load_dotenv()

class Config:
 
    @staticmethod
    def get(key: str, default=None) -> str:
        env = os.getenv("ENV", "dev").upper()  # Default to 'dev' if ENV is not set
        env_key = f"{env}_{key}"
        value = os.getenv(env_key, os.getenv(key, default))  # Try ENV_KEY first, then plain KEY

        if value is None and default is None:
            raise KeyError(f"Configuration key '{env_key}' or '{key}' not found and no default value provided.")
        return value
    
    @property
    def base_url(self) -> str:
        return self.get("BASE_URL")
    
    @property
    def username(self) -> str:
        return self.get("USERNAME")
    
    @property
    def password(self) -> str:
        return self.get("PASSWORD")
    
    @property
    def card_number(self) -> str:
        return self.get("CARD_NUMBER")
    
    @property
    def card_name(self) -> str:
        return self.get("CARD_NAME")
    
settings = Config()