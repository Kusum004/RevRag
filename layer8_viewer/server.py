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

from fastapi.responses import FileResponse, HTMLResponse, Response

@app.get("/api/knowledge-pack")
def get_knowledge_pack():
    pack_file = OUTPUT_DIR / "knowledge_pack.json"
    if not pack_file.exists():
        pack_file = OUTPUT_DIR / "test_knowledge_pack.json"
    if not pack_file.exists():
        raise HTTPException(status_code=404, detail="Knowledge pack not found. Run exploration pipeline first.")
    with open(pack_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Response(
        content=json.dumps(data),
        media_type="application/json",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

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
    clean_name = screen_name.replace(" ", "_").replace("/", "_").lower()
    
    # Check exact clean name
    exact_file = OUTPUT_DIR / f"rebuild_{screen_name.replace(' ', '_').replace('/', '_')}.html"
    if exact_file.exists():
        with open(exact_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
            
    # Case-insensitive search across generated rebuild files
    for p in OUTPUT_DIR.glob("rebuild_*.html"):
        if clean_name in p.stem.lower() or p.stem.lower() in clean_name:
            with open(p, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())

    # Fallback to first available rebuild HTML if any exists
    available_rebuilds = list(OUTPUT_DIR.glob("rebuild_*.html"))
    if available_rebuilds:
        with open(available_rebuilds[0], "r", encoding="utf-8") as f:
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

# Safe UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    print("\n[+] RevRag React + Tailwind Studio running at: http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
