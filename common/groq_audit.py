import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
from common.config import OUTPUT_DIR

AUDIT_LOG_FILE = OUTPUT_DIR / "groq_api_audit_log.jsonl"

def log_groq_call(
    layer: str,
    model: str,
    latency_ms: float,
    input_summary: Dict[str, Any],
    output_summary: Dict[str, Any],
    status: str = "success",
    error_message: Optional[str] = None
):
    """
    Logs auditable Groq API calls for evaluation and jury demonstration.
    Appends structured JSON Lines to output/groq_api_audit_log.jsonl.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": time.time(),
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "layer": layer,
        "model": model,
        "latency_ms": round(latency_ms, 2),
        "status": status,
        "input": input_summary,
        "output": output_summary,
        "error": error_message
    }
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
