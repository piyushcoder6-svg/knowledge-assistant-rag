from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import traceback
from ingest import ingest_pdf
from retriever import get_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

class Question(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "RAG API is running 🚀"}

@app.get("/app")
def serve_frontend():
    return FileResponse("../frontend/index.html")

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = DOCS_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest_pdf(str(file_path))

    return {"message": f"✅ {file.filename} ingested successfully"}

@app.post("/ask")
def ask_question(body: Question):
    try:
        answer = get_answer(body.question)
        return {"answer": answer}
    except Exception as e:
        print("ERROR:", traceback.format_exc())
        return {"error": str(e)}
