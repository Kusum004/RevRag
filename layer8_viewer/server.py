import json
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from common.config import OUTPUT_DIR

app = FastAPI(title="RevRag Zero-Touch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/knowledge-pack")
def get_knowledge_pack():
    pack_file = OUTPUT_DIR / "knowledge_pack.json"
    if not pack_file.exists():
        pack_file = OUTPUT_DIR / "test_knowledge_pack.json"
    if not pack_file.exists():
        raise HTTPException(status_code=404, detail="Knowledge pack not found. Run exploration pipeline first.")
    with open(pack_file, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/screenshot/{fingerprint}")
def get_screenshot(fingerprint: str):
    sc_file = OUTPUT_DIR / f"screenshot_{fingerprint}.png"
    if sc_file.exists():
        return FileResponse(str(sc_file), media_type="image/png")
    raise HTTPException(status_code=404, detail="Screenshot not found")

@app.get("/api/fidelity/{filename}")
def get_fidelity_proof(filename: str):
    proof_file = OUTPUT_DIR / filename
    if proof_file.exists():
        return FileResponse(str(proof_file), media_type="image/png")
    raise HTTPException(status_code=404, detail="Proof image not found")

@app.get("/api/rebuild-html/{screen_name}")
def get_rebuild_html(screen_name: str):
    clean_name = screen_name.replace(" ", "_").replace("/", "_")
    html_file = OUTPUT_DIR / f"rebuild_{clean_name}.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="HTML rebuild not found")

# Serve React Frontend Build
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_react_app(full_path: str):
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        raise HTTPException(status_code=404, detail="Frontend build index not found")

if __name__ == "__main__":
    import uvicorn
    print("\n⚡ RevRag React + Tailwind Studio running at: http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
