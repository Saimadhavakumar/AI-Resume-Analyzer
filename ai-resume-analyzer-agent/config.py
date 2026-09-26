# config.py

import os

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Default model (can change to mistral if needed)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Generation settings
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))

# File upload settings
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# Flask settings
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"