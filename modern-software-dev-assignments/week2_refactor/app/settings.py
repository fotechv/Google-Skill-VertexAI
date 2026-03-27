from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    # Database
    db_path: str = os.getenv("WEEK2_DB_PATH", "")  # optional override; if empty uses ./data/app.db

    # Ollama
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b") # llama3.1:8b
    ollama_timeout_sec: float = float(os.getenv("OLLAMA_TIMEOUT_SEC", "60"))

settings = Settings()
