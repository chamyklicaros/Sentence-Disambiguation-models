import pysbd
from wtpsplit import SaT
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# Load models once at startup
sat_lora_adapted = SaT(
    "sat-3l",
    lora_path="models/wtpsplit/sat-3l-Taglish_lora/facebook-comments/tl",
)
seg = pysbd.Segmenter(language="en", clean=False)
sat_adapted = SaT("sat-12l-sm")

app.mount("/web", StaticFiles(directory="web"), name="web")  # missing leading /

class SentenceRequest(BaseModel):  # was missing entirely
    sentence: str
    model: str

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.post("/analyze")
async def analyze(req: SentenceRequest):
    text = req.sentence.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Input sentence is empty.")

    if req.model == "sat_finetuned":
        result = sat_lora_adapted.split(text)
    elif req.model == "sat":
        result = sat_adapted.split(text)
    elif req.model == "pysbd":
        result = seg.segment(text)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown model: {req.model}")

    return {
        "result": result,
        "model": req.model,
        "sentence": text,
        "count": len(result)
    }