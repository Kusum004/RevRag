import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TESTS_DIR = BASE_DIR / "tests"

# Load .env file automatically if present in project root
try:
    from dotenv import load_dotenv
    env_paths = [BASE_DIR / ".env", BASE_DIR / ".pytest_cache" / ".env", Path.cwd() / ".env"]
    for ep in env_paths:
        if ep.is_file():
            load_dotenv(dotenv_path=ep)
            break
except ImportError:
    pass

# ADB Discovery Paths
COMMON_ADB_PATHS = [
    r"C:\Users\S Kusum\AppData\Local\Android\Sdk\platform-tools\adb.exe",
    r"C:\Android\Sdk\platform-tools\adb.exe",
    os.getenv("ADB_PATH", "adb"),
]

def get_adb_path() -> str:
    """Finds the available adb executable path."""
    for path in COMMON_ADB_PATHS:
        if path and Path(path).is_file():
            return str(path)
    return "adb"

def get_groq_api_key(required: bool = True) -> str:
    """
    Retrieves GROQ_API_KEY from environment.
    If required and missing, raises a clear RuntimeError with actionable instructions.
    """
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key and required:
        raise RuntimeError(
            "\n[!] GROQ_API_KEY IS MISSING!\n"
            "    RevRag requires a real Groq API key for multimodal screen understanding (Layer 4)\n"
            "    and dynamic tone-of-voice synthesis (Layer 5).\n\n"
            "    How to fix:\n"
            "    1. Get a free API key at: https://console.groq.com/keys\n"
            "    2. Set the environment variable in your terminal:\n"
            "       Windows PowerShell: $env:GROQ_API_KEY='gsk_...'\n"
            "       Windows CMD:        set GROQ_API_KEY=gsk_...\n"
            "       Linux / Mac:        export GROQ_API_KEY='gsk_...'\n"
            "    OR create a .env file in the project root with: GROQ_API_KEY=gsk_...\n"
        )
    return key

class AppConfig(BaseModel):
    app_package: str = "com.android.settings"
    mode: str = "adb"  # "adb" is the primary production mode
    step_budget: int = 35
    screenshot_compression_quality: int = 85
    llm_provider: str = "groq"  # "groq" is the primary AI provider
    groq_api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_vision_model: str = "qwen/qwen3.6-27b"
    groq_text_model: str = "llama-3.3-70b-versatile"
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    max_knowledge_pack_size_kb: int = 1500  # Strict < 1.5MB constraint

