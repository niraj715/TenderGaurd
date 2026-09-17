import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "procureshield.db"

# Serverless environment handling (Vercel / AWS Lambda)
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    import shutil
    tmp_db = Path("/tmp/procureshield.db")
    if not tmp_db.exists() and DEFAULT_DB_PATH.exists():
        try:
            shutil.copy2(str(DEFAULT_DB_PATH), str(tmp_db))
        except Exception:
            pass
    default_db_url = f"sqlite:///{tmp_db}"
else:
    default_db_url = f"sqlite:///{DEFAULT_DB_PATH}"

class Settings(BaseSettings):
    PROJECT_NAME: str = "ProcureShield AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "procureshield-super-secret-key-change-in-prod-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", default_db_url)

    WEIGHT_PROCUREMENT: float = 0.20
    WEIGHT_VENDOR_NETWORK: float = 0.15
    WEIGHT_PRICE: float = 0.15
    WEIGHT_EXECUTION: float = 0.15
    WEIGHT_QUALITY: float = 0.15
    WEIGHT_PUBLIC_FEEDBACK: float = 0.10
    WEIGHT_MAINTENANCE: float = 0.10

    THRESHOLD_CRITICAL: int = 90
    THRESHOLD_HIGH: int = 75
    THRESHOLD_MEDIUM: int = 50

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()

