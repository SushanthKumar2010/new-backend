import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

# ---------------- Environment ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash-lite"

# ---------------- Allowed Subjects ----------------
ALLOWED_SUBJECTS = [
    "Telugu", "English", "Hindi",
    "Mathematics", "Science", "Social Studies"
]

CHAPTERS = {
    "Telugu": ["కథలు", "కవిత్వం", "వ్యాకరణం"],
    "English": ["Prose", "Poetry", "Grammar"],
    "Hindi": ["गद्य", "पद्य", "व्याकरण"],
    "Mathematics": [
        "Real Numbers", "Polynomials", "Pair of Linear Equations",
        "Quadratic Equations", "Arithmetic Progressions",
        "Triangles", "Coordinate Geometry"
    ],
    "Science": [
        "Chemical Reactions", "Acids & Bases", "Metals & Non-metals",
        "Carbon Compounds", "Life Processes", "Control & Coordination"
    ],
    "Social Studies": [
        "Nationalism in India", "Industrialization", "Post-War World",
        "Citizenship", "Economic Development"
    ]
}

# ---------------- Prompt Builder ----------------
def build_ap_prompt(class_level: str, subject: str, chapter: str, question: str) -> str:
    return f"""You are an expert AP SSC Class 10 tutor. Format answers cleanly with:

## Main Title
**Definition:** Clear explanation
**Formula:** Show equation clearly  
**Key Points:**
- Bullet 1
- Bullet 2

**Examples:**
1. Example 1
2. Example 2

**Real Life Uses:**
- Application 1
- Application 2

**Common Exam Mistakes:**
- Mistake 1 explanation
- Mistake 2 explanation

Keep answers 4-8 marks length. Use simple Telugu-English mix if needed.

BOARD: AP SSC Class 10
SUBJECT: {subject}
CHAPTER: {chapter}

Student Question:
{question}

Follow AP SSC 2025–26 syllabus only.""".strip()

# ---------------- App Init ----------------
app = FastAPI(title="AP SSC Class 10 AI Tutor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Schemas ----------------
class AskRequest(BaseModel):
    class_level: str = "10"
    subject: str
    chapter: str
    question: str

class AskResponse(BaseModel):
    answer: str
    meta: dict

# ---------------- Routes ----------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/ask", response_model=AskResponse)
async def ask_ap_ssc(payload: AskRequest):
    if payload.subject not in ALLOWED_SUBJECTS:
        raise HTTPException(
            status_code=400,
            detail=f"Subject must be one of {ALLOWED_SUBJECTS}"
        )

    if payload.chapter not in CHAPTERS.get(payload.subject, []):
        raise HTTPException(
            status_code=400,
            detail="Chapter not supported for this subject"
        )

    prompt = build_ap_prompt(
        payload.class_level,
        payload.subject,
        payload.chapter,
        payload.question
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        answer = (response.text or "").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return AskResponse(
        answer=answer,
        meta={
            "class_level": payload.class_level,
            "subject": payload.subject,
            "chapter": payload.chapter
        }
    )
