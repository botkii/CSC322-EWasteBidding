import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    FLASK_KEY = os.getenv("FLASK_KEY", "dev_secret_key")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    DEBUG = True  # Enable for development