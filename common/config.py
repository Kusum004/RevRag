import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TESTS_DIR = BASE_DIR / "tests"

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

class AppConfig(BaseModel):
    app_package: str = "com.android.settings"
    mode: str = "adb"  # "adb" is the primary production mode
    step_budget: int = 30
    screenshot_compression_quality: int = 85
    llm_provider: str = "auto"  # "gemini", "openai", "offline_heuristic"
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    max_knowledge_pack_size_kb: int = 1500  # Strict < 1.5MB constraint
