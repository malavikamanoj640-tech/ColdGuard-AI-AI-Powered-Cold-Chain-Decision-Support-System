import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "data", "enhanced_supply_chain.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models", "supplyshield")
SECRET_KEY = os.environ.get("SUPPLYSHIELD_SECRET", "supplyshield-dev-key")

# XAMPP / MySQL configuration. XAMPP defaults are root with no password.
DB_HOST = os.environ.get("SUPPLYSHIELD_DB_HOST", "127.0.0.1")
DB_PORT = int(os.environ.get("SUPPLYSHIELD_DB_PORT", "3306"))
DB_USER = os.environ.get("SUPPLYSHIELD_DB_USER", "root")
DB_PASSWORD = os.environ.get("SUPPLYSHIELD_DB_PASSWORD", "")
DB_NAME = os.environ.get("SUPPLYSHIELD_DB_NAME", "supplyshield_ai")
DB_PATH = f"mysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"  # display-only compatibility

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/generate')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen2.5:0.5b')
OLLAMA_HOST = OLLAMA_URL.rsplit('/api/generate', 1)[0].rstrip('/')
OLLAMA_TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', '30'))
