# config.py

import os

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Default model (can change to mistral if needed)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Generation settings
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 800))