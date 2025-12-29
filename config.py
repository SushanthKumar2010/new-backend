import os

# ---------------- Gemini API Setup ----------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash-lite"  # Free tier model with good quota

# ---------------- AP SSC Class 10 Subjects ----------------
ALLOWED_SUBJECTS = [
    "Telugu",
    "English",
    "Hindi",
    "Mathematics",
    "Science",
    "Social Studies"
]

# ---------------- AP SSC Class 10 Chapters ----------------
CHAPTERS = {
    "Telugu": [
        "కథలు (Stories)",
        "కవిత్వం (Poetry)",
        "వ్యాకరణం (Grammar)",
        "నాటకం (Drama)",
        "ఆధునిక సాహిత్యం (Modern Literature)"
    ],
    "English": [
        "Prose",
        "Poetry",
        "Grammar",
        "Writing Skills",
        "Reading Comprehension"
    ],
    "Hindi": [
        "गद्य खंड (Prose)",
        "पद्य खंड (Poetry)",
        "व्यాకరణ (Grammar)",
        "निबंध लेखन (Essay Writing)"
    ],
    "Mathematics": [
        "Real Numbers",
        "Polynomials",
        "Pair of Linear Equations",
        "Quadratic Equations",
        "Arithmetic Progressions",
        "Triangles",
        "Coordinate Geometry",
        "Trigonometry"
    ],
    "Science": [
        "Chemical Reactions",
        "Acids Bases Salts",
        "Metals Non-metals",
        "Carbon Compounds",
        "Life Processes",
        "Control Coordination",
        "Reproduction",
        "Heredity",
        "Our Environment"
    ],
    "Social Studies": [
        "Nationalism in India",
        "Industrialization 1857-1947",
        "Post-war World",
        "Citizenship",
        "Economic Development",
        "Climate Disaster Management"
    ]
}

# ---------------- Validate API Key ----------------
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")
