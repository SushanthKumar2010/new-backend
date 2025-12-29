import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

# ======================
# CONFIG
# ======================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

MODEL_NAME = "gemini-2.5-flash-lite"

# ======================
# APP SETUP
# ======================

app = FastAPI(
    title="ICSE AI Tutor",
    description="FastAPI backend for Andhra Pradesh SSC Class 10 tutor using Gemini",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# GEMINI CLIENT
# ======================

client = genai.Client(api_key=GEMINI_API_KEY)

# ======================
# SCHEMAS
# ======================

class AskRequest(BaseModel):
    class_level: str = "10"
    subject: str = "General"
    chapter: str = "General"
    question: str


class AskResponse(BaseModel):
    answer: str
    meta: dict

# ======================
# ROUTES
# ======================

@app.get("/")
def root():
    return {"status": "Backend running ✅"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
async def ask_icse_question(payload: AskRequest):

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    prompt = f"""
You are an expert ICSE Class {payload.class_level} tutor.

Subject: {payload.subject}
Chapter: {payload.chapter}

Student Question:
\"\"\"{payload.question}\"\"\"  

Instructions:
1. Explain concepts clearly as per AP SSC syllabus
2. Provide step-by-step solutions
3. Show proper calculations and working
4. Use AP SSC exam-oriented methods
5. Mention common mistakes students make
6. Structure the answer for maximum marks
7. Use simple language suitable for Class 10 students
""".strip()

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        answer = (response.text or "").strip()
        if not answer:
            answer = "I could not generate an answer. Please try again."

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

    return AskResponse(
        answer=answer,
        meta={
            "class_level": payload.class_level,
            "subject": payload.subject,
            "chapter": payload.chapter,
        },
    )

# ======================
# LOCAL DEV ONLY
# ======================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
