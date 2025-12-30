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
    title="CBSE AI Tutor",
    description="FastAPI backend for CBSE Class 10 NCERT tutor using Gemini",
    version="2.0.0",
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
    return {"status": "CBSE Backend running ✅"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
async def ask_cbse_question(payload: AskRequest):

    # ---------- Input validation ----------
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    # ---------- CBSE-Optimized Prompt ----------
    prompt = f"""
You are an expert CBSE Class {payload.class_level} NCERT tutor.

Subject: {payload.subject}
Chapter: {payload.chapter}

Student Question:
\"\"\"{payload.question.strip()}\"\"\"  

STRICT ANSWERING RULES (MUST FOLLOW):
1. Use ONLY plain text (NO LaTeX, NO $, NO symbols like ^, /, = unless absolutely necessary)
2. Write angles in words (example: 30 degrees, not 30° or 30^)
3. Write fractions in words (example: one by two, not 1/2)
4. Use simple CBSE Class 10 language
5. Keep the answer SHORT but CONCEPTUALLY DEEP
6. Prefer bullet points with simple words (* or - only)
7. Explain the core idea first
8. Add ONE simple example if helpful
9. Avoid unnecessary theory or repetition
10. Be NCERT and exam-oriented
11. Do NOT use emojis
12. Do NOT mention AI, Gemini, LaTeX, or formatting terms

Preferred Structure:
- Core idea
- Explanation (2 to 4 lines)
- Final value or result (in words)
- Key exam point
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
            answer = "Unable to generate an answer right now. Please try again."

    except Exception as e:
        print("❌ Gemini failure:", str(e))
        raise HTTPException(
            status_code=500,
            detail="AI service is temporarily unavailable. Please retry."
        )

    return AskResponse(
        answer=answer,
        meta={
            "board": "CBSE",
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

