"""Configuración central de CodificaMed."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    def __init__(self) -> None:
        self.llm_provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

        # Ollama local
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        self.ollama_num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "4096"))
        self.ollama_timeout = float(os.getenv("OLLAMA_TIMEOUT", "300"))

        # Claude API
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

        # Búsqueda catálogo
        self.index_mode = os.getenv("INDEX_MODE", "lexico").strip().lower()

        # Rutas y almacenamiento
        self.data_dir = BASE_DIR / "data"
        self.db_path = self.data_dir / "codificamed.db"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.puerto = int(os.getenv("PUERTO", "8001"))


settings = Settings()
