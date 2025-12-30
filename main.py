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
    description="FastAPI backend for AP SSC / ICSE Class 10 tutor using Gemini",
    version="1.1.1",
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

    # ---------- Input validation ----------
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    prompt = f"""
You are an expert ICSE / AP SSC Class {payload.class_level} tutor.

Subject: {payload.subject}
Chapter: {payload.chapter}

Student Question:
\"\"\"{payload.question.strip()}\"\"\"  

Instructions:
1. Explain concepts clearly as per AP SSC syllabus
2. Use simple Class 10 language
3. Always use ₹ symbol instead of $ (what ever the topic is)
""".strip()

    print("📩 Question received:", payload.question)

    # ---------- Gemini call ----------
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        answer = ""

        # SAFE extraction
        if response:
            if hasattr(response, "text") and response.text:
                answer = response.text.strip()
            elif hasattr(response, "candidates") and response.candidates:
                answer = response.candidates[0].content.parts[0].text.strip()

        if not answer:
            answer = "I could not generate an answer at the moment. Please try again."

    except Exception as e:
        # LOG real error (Render logs)
        print("❌ Gemini failure:", str(e))

        # RETURN safe message to frontend
        raise HTTPException(
            status_code=500,
            detail="AI service is temporarily unavailable. Please retry."
        )

    return AskResponse(
        answer=answer,
        meta={
            "class_level": payload.class_level,
            "subject": payload.subject,
            "chapter": payload.chapter,
        },
    )


# ======================
# LOCAL DEV
# ======================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)



