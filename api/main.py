from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import os

from TTS.api import TTS
from github import Github

app = FastAPI(title="Bangla+English TTS API by DevZeron")

# ---------- CONFIG ----------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # set in Vercel env
REPO_NAME = "CodeDevZeron/Zeron"
REPO_PATH = "Zeron"  # folder inside repo
BRANCH = "main"

# ---------- INIT ----------
tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
TMP = Path("/tmp")
TMP.mkdir(exist_ok=True)

# ---------- FUNCTIONS ----------
def upload_to_github(text: str):
    # 1. Generate TTS audio
    audio_file = TMP / f"{uuid.uuid4().hex}.wav"
    tts.tts_to_file(text=text, file_path=str(audio_file))

    # 2. Connect GitHub
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    # 3. Read file bytes
    with open(audio_file, "rb") as f:
        content = f.read()

    # 4. Commit file
    filename = f"tts_{uuid.uuid4().hex}.wav"
    repo.create_file(
        f"{REPO_PATH}/{filename}",
        f"TTS generated for text: {text}",
        content,
        branch=BRANCH
    )

    # 5. Return raw GitHub URL
    raw_url = f"https://raw.githubusercontent.com/{REPO_NAME}/{BRANCH}/{REPO_PATH}/{filename}"
    return raw_url

# ---------- ROUTES ----------
@app.get("/health")
def health():
    return {"status": "ok", "api_by": "DevZeron"}

@app.get("/tts")
async def tts_get(text: str = None):
    if not text:
        return JSONResponse({"error": "text parameter is required", "api_by": "DevZeron"}, status_code=400)
    file_url = upload_to_github(text)
    return {
        "api_by": "DevZeron",
        "text": text,
        "audio_url": file_url
    }

@app.post("/tts")
async def tts_post(text: str = Form(...)):
    file_url = upload_to_github(text)
    return {
        "api_by": "DevZeron",
        "text": text,
        "audio_url": file_url
    }
