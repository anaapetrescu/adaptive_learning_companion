"""
Adaptive AI Learning Companion — v3
====================================
New in v3:
  • Multiple choice + open-ended question type selector
  • Difficulty levels (Easy / Medium / Hard) for exercises and tests
  • Countdown timer on tests with auto-submit
  • Flashcard generation and flip UI after study guide
  • Teacher Chat (general + contextual ask-about-this)
  • Notebook with dated sessions and example pre-filled notes
  • Rubric-style grading for open-ended answers
  • Deterministic auto-grading for multiple choice
"""

import os
import re
import random
import json
import time
import streamlit as st
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, date

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
<style>
#MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}
.block-container{padding-top:1.5rem;padding-bottom:2rem;}
.stApp{background:#F0F4F8;}

/* Hero */
.hero-wrap{background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 55%,#0F172A 100%);
  border-radius:24px;padding:70px 48px 60px;text-align:center;margin-bottom:28px;}
.hero-badge{display:inline-block;background:rgba(99,102,241,.25);color:#A5B4FC;
  border:1px solid rgba(165,180,252,.3);padding:5px 16px;border-radius:20px;
  font-size:.72rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:20px;}
.hero-title{font-size:2.8rem;font-weight:800;color:#fff;margin:0 0 14px;line-height:1.18;}
.hero-sub{font-size:1.05rem;color:#94A3B8;max-width:520px;margin:0 auto;line-height:1.65;}

/* Feat pills */
.feat-pill{background:white;border:1px solid #E2E8F0;border-radius:14px;padding:22px 16px;text-align:center;}
.feat-icon{font-size:1.7rem;margin-bottom:8px;}
.feat-title{color:#1E293B;font-size:.85rem;font-weight:700;}
.feat-desc{color:#64748B;font-size:.75rem;margin-top:5px;line-height:1.4;}

/* Top bar */
.top-bar-title{font-size:1.05rem;font-weight:700;color:#1E293B;}
.top-bar-sub{font-size:.78rem;color:#94A3B8;margin-top:1px;}

/* Cards */
.course-card{background:white;border-radius:14px;padding:20px 24px;
  box-shadow:0 1px 5px rgba(0,0,0,.06);border-left:5px solid #6366F1;}
.course-title{font-size:1.05rem;font-weight:700;color:#1E293B;margin:0 0 5px;}
.course-meta{font-size:.8rem;color:#64748B;margin:0;}
.s-card{background:white;border-radius:14px;padding:24px;
  box-shadow:0 1px 5px rgba(0,0,0,.05);margin-bottom:18px;}
.m-card{background:white;border-radius:12px;padding:20px;text-align:center;
  box-shadow:0 1px 5px rgba(0,0,0,.05);}
.m-value{font-size:1.9rem;font-weight:800;color:#1E293B;line-height:1;}
.m-label{font-size:.78rem;color:#64748B;font-weight:500;margin-top:5px;}
.m-cat{font-size:.82rem;margin-top:4px;color:#64748B;}

/* Progress */
.prog-track{background:#E2E8F0;border-radius:20px;height:9px;overflow:hidden;}
.prog-fill{height:100%;border-radius:20px;}

/* Accuracy / info boxes */
.acc-box{background:#FFFBEB;border:1px solid #FDE68A;border-left:4px solid #F59E0B;
  border-radius:10px;padding:14px 18px;margin:14px 0;}
.acc-title{font-weight:700;color:#92400E;font-size:.85rem;margin-bottom:5px;}
.acc-body{color:#78350F;font-size:.82rem;line-height:1.6;}
.pipe-box{background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #3B82F6;
  border-radius:10px;padding:14px 18px;margin:14px 0;}
.pipe-title{font-weight:700;color:#1E40AF;font-size:.85rem;margin-bottom:5px;}
.pipe-body{color:#1E3A8A;font-size:.82rem;line-height:1.65;}
.q-error{background:#FFF1F2;border:1px solid #FECDD3;border-left:4px solid #F43F5E;
  border-radius:10px;padding:18px 22px;margin:10px 0;}
.q-error-title{font-weight:700;color:#E11D48;font-size:.95rem;margin-bottom:7px;}
.q-error-body{color:#475569;font-size:.86rem;line-height:1.65;}

/* Question cards */
.q-card{background:white;border-radius:12px;padding:18px 22px;
  box-shadow:0 1px 5px rgba(0,0,0,.05);margin-bottom:10px;}
.q-num{font-weight:700;color:#1E293B;font-size:.88rem;margin-bottom:7px;}
.q-text{color:#334155;font-size:.93rem;line-height:1.5;}

/* MC option */
.mc-correct{background:#D1FAE5;border:2px solid #10B981;border-radius:9px;
  padding:10px 14px;margin:4px 0;color:#065F46;font-weight:600;}
.mc-wrong{background:#FEE2E2;border:2px solid #F87171;border-radius:9px;
  padding:10px 14px;margin:4px 0;color:#7F1D1D;}
.mc-neutral{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:9px;
  padding:10px 14px;margin:4px 0;color:#334155;}

/* Flashcard */
.fc-front{background:linear-gradient(135deg,#6366F1,#4F46E5);border-radius:16px;
  padding:40px 30px;text-align:center;color:white;min-height:200px;
  display:flex;flex-direction:column;justify-content:center;}
.fc-back{background:white;border:2px solid #6366F1;border-radius:16px;
  padding:40px 30px;text-align:center;color:#1E293B;min-height:200px;
  display:flex;flex-direction:column;justify-content:center;}
.fc-label{font-size:.7rem;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;opacity:.7;margin-bottom:12px;}
.fc-text{font-size:1.1rem;font-weight:600;line-height:1.5;}

/* Chat */
.chat-user{background:#6366F1;color:white;border-radius:14px 14px 4px 14px;
  padding:10px 16px;margin:6px 0;max-width:80%;margin-left:auto;font-size:.88rem;}
.chat-ai{background:white;border:1px solid #E2E8F0;color:#1E293B;
  border-radius:14px 14px 14px 4px;padding:10px 16px;margin:6px 0;
  max-width:85%;font-size:.88rem;box-shadow:0 1px 4px rgba(0,0,0,.06);}

/* Timer */
.timer-ok{background:#D1FAE5;border-radius:10px;padding:10px 20px;
  text-align:center;font-size:1.4rem;font-weight:800;color:#065F46;}
.timer-warn{background:#FEF3C7;border-radius:10px;padding:10px 20px;
  text-align:center;font-size:1.4rem;font-weight:800;color:#92400E;}
.timer-danger{background:#FEE2E2;border-radius:10px;padding:10px 20px;
  text-align:center;font-size:1.4rem;font-weight:800;color:#7F1D1D;}

/* Difficulty badges */
.diff-easy{background:#D1FAE5;color:#065F46;border-radius:8px;
  padding:3px 10px;font-size:.75rem;font-weight:700;}
.diff-medium{background:#FEF3C7;color:#92400E;border-radius:8px;
  padding:3px 10px;font-size:.75rem;font-weight:700;}
.diff-hard{background:#FEE2E2;color:#7F1D1D;border-radius:8px;
  padding:3px 10px;font-size:.75rem;font-weight:700;}

/* Notebook */
.nb-session-card{background:white;border-radius:12px;padding:18px 22px;
  box-shadow:0 1px 5px rgba(0,0,0,.05);border-left:4px solid #6366F1;margin-bottom:12px;}
.nb-session-date{font-size:.75rem;color:#94A3B8;font-weight:600;
  text-transform:uppercase;letter-spacing:.5px;}
.nb-session-title{font-size:.95rem;font-weight:700;color:#1E293B;margin:3px 0;}

/* Sidebar */
.sb-course-box{background:#0F172A;border-radius:10px;padding:14px 16px;margin-bottom:14px;}
.sb-course-label{color:#475569;font-size:.66rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.8px;}
.sb-course-name{color:white;font-weight:700;font-size:.95rem;margin-top:3px;}
.sb-section-label{color:#334155;font-size:.66rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.8px;margin:14px 0 6px 4px;}
.file-tag{background:#1E3A5F;border-radius:8px;padding:7px 12px;color:#93C5FD;
  font-size:.76rem;margin-bottom:4px;display:block;}
.file-chip{display:inline-block;background:#EEF2FF;color:#4338CA;border-radius:20px;
  padding:5px 13px;font-size:.78rem;font-weight:600;margin:3px;}
.nb-header{background:#1E293B;color:white;border-radius:10px 10px 0 0;
  padding:12px 18px;font-weight:700;font-size:.85rem;}

/* Widgets */
.stTextArea textarea{border-radius:10px;border-color:#E2E8F0;
  font-size:.88rem;line-height:1.6;background:#FAFAFA;}
.stTextArea textarea:focus{border-color:#6366F1;
  box-shadow:0 0 0 3px rgba(99,102,241,.1);}
.stButton>button{border-radius:9px;font-weight:600;transition:all .18s;}
.stButton>button:hover{transform:translateY(-1px);
  box-shadow:0 3px 10px rgba(0,0,0,.12);}
.stAlert{border-radius:10px;}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────

EXAMPLE_NOTES = [
    {
        "id": "ex1",
        "date": "2026-02-10",
        "title": "Session 1 — R Basics",
        "content": (
            "Key things I need to remember:\n"
            "- Everything in R is an object. Use <- for assignment, not =\n"
            "- Data types: vector, matrix, list, dataframe (tibble is cleaner)\n"
            "- Indexing: [row, column] — always row first!\n"
            "- iris[2, ] = entire row 2. iris[, 1] = entire first column.\n"
            "- $ operator is the easiest way to grab a column: iris$Petal.Width\n\n"
            "Questions I still have:\n"
            "- When should I use list() vs c()?\n"
            "- What's the difference between data.frame and tibble in practice?"
        ),
    },
    {
        "id": "ex2",
        "date": "2026-02-17",
        "title": "Session 2 — Pipe and Functions",
        "content": (
            "The pipe %>% is the most important thing from this session.\n"
            "Read it as 'AND THEN'. Ctrl+Shift+M is the shortcut.\n\n"
            "Without pipe (hard to read):\n"
            "round(prop.table(table(sample(c(1,0), 100, T, c(.75,.25)))), 2)\n\n"
            "With pipe (natural):\n"
            "c(1,0) %>% sample(100,T,c(.75,.25)) %>% table() %>% prop.table() %>% round(2)\n\n"
            "Writing functions: use function(params) { ... }\n"
            "replicate() = run the same experiment n times. Great for simulations.\n\n"
            "TODO: practice writing my own function from scratch before next class."
        ),
    },
]


def init_session_state():
    defaults = {
        "page":          "landing",
        "courses":       {},
        "active_course": None,
        "nav_section":   "files",
        "global_chat":   [],       # list of {role, content}
        "context_chat":  [],       # contextual chat messages
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_course():
    n = st.session_state.active_course
    if n and n in st.session_state.courses:
        return st.session_state.courses[n]
    return None


def set_key(key, value):
    n = st.session_state.active_course
    if n and n in st.session_state.courses:
        st.session_state.courses[n][key] = value


def empty_course():
    return {
        "chunks":             [],
        "file_names":         [],
        "study_guide":        "",
        "flashcards":         [],      # list of {front, back}
        "exercises":          [],      # list of question dicts
        "exercise_answers":   {},
        "exercise_grades":    [],
        "test_questions":     [],      # list of question dicts
        "test_answers":       {},
        "test_grades":        [],
        "test_start_time":    None,
        "test_submitted":     False,
        "diagnostic":         "",
        "notebook_sessions":  list(EXAMPLE_NOTES),  # pre-fill with examples
    }


def go(page, section=None):
    st.session_state.page = page
    if section:
        st.session_state.nav_section = section


# ──────────────────────────────────────────────────────────────────────────────
# AI — GEMINI WITH ERROR HANDLING
# ──────────────────────────────────────────────────────────────────────────────

# Models tried in order — first one that works is cached for the session
GEMINI_MODEL_CANDIDATES = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-pro",
]


def get_working_model(temperature=0.7):
    """
    Try Gemini model names in order and return the first one that works.
    Caches the working model name in session_state so we only probe once.
    """
    if "working_model" in st.session_state and st.session_state.working_model:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            m = genai.GenerativeModel(
                model_name=st.session_state.working_model,
                system_instruction=(
                    "You are an expert educational AI assistant. "
                    "Always base your responses strictly on provided course material. "
                    "Never add external information not in the material."
                ),
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1400,
                ),
            )
            return m
        except Exception:
            st.session_state.working_model = None

    genai.configure(api_key=GEMINI_API_KEY)
    for name in GEMINI_MODEL_CANDIDATES:
        try:
            m = genai.GenerativeModel(
                model_name=name,
                system_instruction=(
                    "You are an expert educational AI assistant. "
                    "Always base your responses strictly on provided course material. "
                    "Never add external information not in the material."
                ),
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1400,
                ),
            )
            # Quick test call to verify the model actually works
            m.generate_content("Say OK")
            st.session_state.working_model = name
            return m
        except Exception:
            continue
    return None


def call_ai(prompt, temperature=0.7):
    if not GEMINI_API_KEY:
        st.markdown("""<div class="q-error">
        <div class="q-error-title">⚠️ No Gemini API Key</div>
        <div class="q-error-body">Add <code>GEMINI_API_KEY=your-key</code>
        to your <code>.env</code> file.</div></div>""", unsafe_allow_html=True)
        return ""
    try:
        model = get_working_model(temperature)
        if model is None:
            st.markdown("""<div class="q-error">
            <div class="q-error-title">🔄 No Working Gemini Model Found</div>
            <div class="q-error-body">
            Could not connect to any Gemini model. Please check:<br>
            1. Your API key is correct in <code>.env</code><br>
            2. Billing is active at <b>console.cloud.google.com</b><br>
            3. Your internet connection is working<br><br>
            Then restart the app with <code>streamlit run app.py</code>
            </div></div>""", unsafe_allow_html=True)
            return ""
        return model.generate_content(prompt).text
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower() or "resource_exhausted" in err.lower():
            st.markdown("""<div class="q-error">
            <div class="q-error-title">⏱️ Rate Limit — Wait and Retry</div>
            <div class="q-error-body">Wait 60 seconds then try again.</div>
            </div>""", unsafe_allow_html=True)
        elif "401" in err or "invalid" in err.lower() or "api_key" in err.lower():
            st.error("🔑 Invalid API key. Check your .env file contains: GEMINI_API_KEY=your-key")
        elif "503" in err or "unavailable" in err.lower():
            st.error("⏳ Gemini servers busy. Wait 30 seconds and try again.")
        else:
            # Reset cached model on any unexpected error so next call re-probes
            st.session_state.working_model = None
            st.error(f"Error: {err}")
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# PDF PROCESSING
# ──────────────────────────────────────────────────────────────────────────────

def extract_single_pdf(f):
    text = ""
    try:
        with pdfplumber.open(f) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except Exception as e:
        st.warning(f"Problem reading {f.name}: {e}")
    return text.strip()


def process_multiple_pdfs(files):
    combined, names = "", []
    for f in files:
        t = extract_single_pdf(f)
        if t.strip():
            combined += f"\n\n=== DOCUMENT: {f.name} ===\n\n{t}\n\n"
            names.append(f.name)
    if not combined.strip():
        return [], [], 0
    wc     = len(combined.split())
    chunks = chunk_text(combined)
    return chunks, names, wc


def chunk_text(text, size=800):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]


def get_context(chunks, max_chunks=2):
    ctx   = "\n\n---\n\n".join(chunks[:max_chunks])
    words = ctx.split()
    return " ".join(words[:1400]) if len(words) > 1400 else ctx


# ──────────────────────────────────────────────────────────────────────────────
# DIFFICULTY HELPERS
# ──────────────────────────────────────────────────────────────────────────────

DIFFICULTY_DESCRIPTIONS = {
    "Easy":   "basic recall and straightforward definitions. Distractors should be clearly wrong.",
    "Medium": "conceptual understanding and simple application. Distractors should be plausible.",
    "Hard":   "deep analysis, integration of multiple concepts, and nuanced distinctions. "
              "Distractors should be subtle and require careful reasoning to eliminate.",
}

TIMER_DURATIONS = {"Easy": 8, "Medium": 5, "Hard": 3}   # minutes per question


# ──────────────────────────────────────────────────────────────────────────────
# CONTENT GENERATION
# ──────────────────────────────────────────────────────────────────────────────

def generate_study_guide(context, tone, depth, fmt):
    prompt = f"""Create a study guide from this material ONLY.

PREFERENCES — Tone: {tone} | Depth: {depth} | Format: {fmt}

MATERIAL:
{context}

Rules:
- Simple language = plain words. Academic = formal terms.
- Overview = concise. Detailed = elaborate with examples from text.
- Structured headings = ## / ### markdown. Bullets = bullet lists. Paragraphs = prose.
- End with "## Key Takeaways" listing 3-5 main ideas.

Write now:"""
    return call_ai(prompt, 0.5)


def generate_flashcards(context, study_guide):
    prompt = f"""Generate exactly 8 flashcards from this study guide and material.

STUDY GUIDE:
{study_guide[:800]}

MATERIAL:
{context}

Each flashcard must have a FRONT (concept/question, max 15 words) and a BACK (clear explanation, max 40 words).

Respond ONLY with valid JSON — no markdown, no code fences, no extra text.
Format exactly like this:
[
  {{"front": "question or concept here", "back": "explanation here"}},
  {{"front": "...", "back": "..."}}
]"""
    raw = call_ai(prompt, 0.4)
    if not raw:
        return []
    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        cards = json.loads(clean)
        if isinstance(cards, list):
            return [c for c in cards if "front" in c and "back" in c]
    except Exception:
        pass
    return []


def generate_mc_questions(context, difficulty, count=5):
    """Generate multiple choice questions. Returns list of dicts."""
    diff_desc = DIFFICULTY_DESCRIPTIONS.get(difficulty, DIFFICULTY_DESCRIPTIONS["Medium"])
    prompt = f"""Generate exactly {count} multiple choice questions from this material ONLY.

DIFFICULTY: {difficulty} — focus on {diff_desc}

MATERIAL:
{context}

Each question must have exactly 4 options (A, B, C, D) and one correct answer.
For Hard difficulty, make distractors subtle and plausible.

Respond ONLY with valid JSON — no markdown, no code fences:
[
  {{
    "question": "question text here",
    "options": {{"A": "option A", "B": "option B", "C": "option C", "D": "option D"}},
    "correct": "A",
    "explanation": "brief explanation of why A is correct"
  }}
]"""
    raw = call_ai(prompt, 0.5)
    if not raw:
        return []
    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        qs = json.loads(clean)
        if isinstance(qs, list):
            # Shuffle options for each question
            result = []
            for q in qs:
                if "question" in q and "options" in q and "correct" in q:
                    items  = list(q["options"].items())
                    random.shuffle(items)
                    # Remap correct answer to new position
                    old_correct_text = q["options"].get(q["correct"], "")
                    new_opts = {}
                    new_correct = q["correct"]
                    for new_letter, (old_letter, text) in zip(
                            ["A","B","C","D"], items):
                        new_opts[new_letter] = text
                        if text == old_correct_text:
                            new_correct = new_letter
                    q["options"]  = new_opts
                    q["correct"]  = new_correct
                    result.append(q)
            return result
    except Exception:
        pass
    return []


def generate_open_questions(context, difficulty, count=5, is_test=False):
    """Generate open-ended questions. Returns list of dicts."""
    diff_desc = DIFFICULTY_DESCRIPTIONS.get(difficulty, DIFFICULTY_DESCRIPTIONS["Medium"])
    if is_test:
        structure = """Questions 1-2: Conceptual
Question 3: Applied scenario
Question 4: Analysis
Question 5: Integrative (connect 2+ ideas)"""
    else:
        structure = """Questions 1-4: Conceptual
Questions 5+: Applied scenario"""

    prompt = f"""Generate exactly {count} open-ended questions from this material ONLY.

DIFFICULTY: {difficulty} — {diff_desc}

STRUCTURE:
{structure}

MATERIAL:
{context}

Respond ONLY with valid JSON:
[
  {{
    "question": "question text",
    "type": "Conceptual",
    "rubric_focus": "what a good answer should address"
  }}
]"""
    raw = call_ai(prompt, 0.5)
    if not raw:
        return []
    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        qs = json.loads(clean)
        if isinstance(qs, list):
            return [q for q in qs if "question" in q]
    except Exception:
        pass
    return []


def grade_mc(question_dict, student_answer):
    """Deterministic grading for multiple choice."""
    correct = question_dict.get("correct", "")
    is_correct = student_answer == correct
    return {
        "score":       10 if is_correct else 0,
        "is_correct":  is_correct,
        "student":     student_answer,
        "correct":     correct,
        "explanation": question_dict.get("explanation", ""),
        "question":    question_dict.get("question", ""),
        "options":     question_dict.get("options", {}),
    }


def grade_open(context, question_dict, answer):
    """Rubric-style grading for open-ended answers."""
    if not answer or not answer.strip():
        return {
            "score":     0,
            "strengths": "No answer provided.",
            "weaknesses": "Answer was blank.",
            "revision":  "Attempt the question using the study material.",
            "question":  question_dict.get("question", ""),
            "answer":    answer,
        }
    rubric = question_dict.get("rubric_focus", "")
    prompt = f"""Grade this student answer using the course material and rubric below.

MATERIAL:
{context}

QUESTION: {question_dict.get("question", "")}
RUBRIC FOCUS: {rubric}
STUDENT ANSWER: {answer}

Grade on a scale 0-10 and provide structured feedback.

Respond ONLY in this exact format:
SCORE: [0-10]
STRENGTHS: [what the student got right]
WEAKNESSES: [what was missing or wrong]
REVISION: [specific advice for improvement]"""
    raw = call_ai(prompt, 0.2)
    score, strengths, weaknesses, revision = 0, "", "", ""
    if raw:
        sm = re.search(r"SCORE:\s*(\d+)", raw)
        stm = re.search(r"STRENGTHS:\s*(.*?)(?=WEAKNESSES:|$)", raw, re.DOTALL)
        wm  = re.search(r"WEAKNESSES:\s*(.*?)(?=REVISION:|$)", raw, re.DOTALL)
        rvm = re.search(r"REVISION:\s*(.*)", raw, re.DOTALL)
        if sm:  score     = min(10, max(0, int(sm.group(1))))
        if stm: strengths = stm.group(1).strip()
        if wm:  weaknesses = wm.group(1).strip()
        if rvm: revision  = rvm.group(1).strip()
    return {
        "score":     score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "revision":  revision,
        "question":  question_dict.get("question", ""),
        "answer":    answer,
    }


def generate_diagnostic(context, grades, q_type):
    summary = ""
    for i, g in enumerate(grades, 1):
        if q_type == "Multiple Choice":
            summary += (f"\nQ{i}: {g['question']}\n"
                        f"Student chose: {g.get('student','?')} | "
                        f"Correct: {g.get('correct','?')} | "
                        f"Score: {g['score']}/10\n---")
        else:
            summary += (f"\nQ{i}: {g['question']}\n"
                        f"Answer: {g.get('answer','')}\n"
                        f"Score: {g['score']}/10\n"
                        f"Weaknesses: {g.get('weaknesses','')}\n---")

    prompt = f"""Write a diagnostic report based on this student performance.

MATERIAL:
{context}

PERFORMANCE:
{summary}

Write with these exact sections:
## Performance Overview
## Knowledge Gaps
## Strengths
## Recommended Actions
## Focus for Next Session

Be specific. Reference actual concepts. No generic advice."""
    return call_ai(prompt, 0.4)


def chat_with_teacher(context, messages):
    """General teacher chat grounded in course material."""
    history = "\n".join([
        f"{'Student' if m['role']=='user' else 'Teacher'}: {m['content']}"
        for m in messages[:-1]
    ])
    latest = messages[-1]["content"] if messages else ""
    prompt = f"""You are an AI teacher. Answer the student's question based ONLY on the course material.
Be clear, encouraging, and use examples from the material.

COURSE MATERIAL:
{context}

CONVERSATION HISTORY:
{history}

STUDENT'S QUESTION: {latest}

Give a clear, helpful answer grounded in the material:"""
    return call_ai(prompt, 0.6)


def contextual_chat(context, highlighted_text, messages):
    """Chat about a specific piece of highlighted text."""
    history = "\n".join([
        f"{'Student' if m['role']=='user' else 'Teacher'}: {m['content']}"
        for m in messages[:-1]
    ])
    latest = messages[-1]["content"] if messages else ""
    prompt = f"""You are an AI teacher explaining a specific concept to a student.

COURSE MATERIAL:
{context}

THE STUDENT IS ASKING ABOUT THIS SPECIFIC TEXT:
"{highlighted_text}"

CONVERSATION HISTORY:
{history}

STUDENT'S QUESTION: {latest}

Explain clearly, staying focused on the highlighted text and the course material:"""
    return call_ai(prompt, 0.6)


# ──────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def score_summary(grades):
    if not grades:
        return 0.0, "Not attempted"
    avg = sum(g["score"] for g in grades) / len(grades)
    if   avg >= 8.5: cat = "🏆 Excellent"
    elif avg >= 7.0: cat = "✅ Good"
    elif avg >= 5.0: cat = "⚠️ Moderate"
    else:            cat = "❌ Needs Improvement"
    return round(avg, 1), cat


def progress_bar_html(pct, color="#6366F1"):
    return (f'<div class="prog-track">'
            f'<div class="prog-fill" style="width:{pct}%;background:{color};"></div>'
            f'</div>')


def show_accuracy_disclaimer():
    st.markdown("""<div class="acc-box">
    <div class="acc-title">⚠️ About AI Grading</div>
    <div class="acc-body">
    Multiple choice is graded deterministically (always accurate).
    Open-ended grading uses AI evaluation which may vary between runs.
    Use open-ended scores as guidance, not final grades.
    </div></div>""", unsafe_allow_html=True)


def show_pipeline_explainer(wc, cc, fc):
    st.markdown(f"""<div class="pipe-box">
    <div class="pipe-title">🔧 Pipeline Overview</div>
    <div class="pipe-body">
    <b>Extraction:</b> {fc} PDF(s) → {wc:,} words extracted via pdfplumber.<br>
    <b>Chunking:</b> Split into {cc} chunks (~800 words each) to fit AI context window.<br>
    <b>Context selection:</b> Top 2 chunks (~1,400 words) sent per AI call — simplified RAG.<br>
    <b>Limitation:</b> Only the first ~1,400 words are used per request.
    </div></div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# NAVIGATION
# ──────────────────────────────────────────────────────────────────────────────

def render_top_bar(title, subtitle=""):
    c0, c1, c2, c3 = st.columns([0.5, 5, 1.2, 1.2])
    with c0:
        if st.button("🏠", key="tb_home"):
            go("landing"); st.rerun()
    with c1:
        st.markdown(f'<div style="padding:6px 0;">'
                    f'<div class="top-bar-title">{title}</div>'
                    f'<div class="top-bar-sub">{subtitle}</div></div>',
                    unsafe_allow_html=True)
    with c2:
        if st.button("📚 Courses", key="tb_courses"):
            go("dashboard"); st.rerun()
    with c3:
        if get_course() and st.button("📓 Notebook", key="tb_nb"):
            go("notebook"); st.rerun()


def render_sidebar():
    course = get_course()
    if not course:
        return
    active = st.session_state.nav_section
    with st.sidebar:
        st.markdown(f'<div class="sb-course-box">'
                    f'<div class="sb-course-label">Active Course</div>'
                    f'<div class="sb-course-name">{st.session_state.active_course}</div>'
                    f'</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-section-label">Workspace</div>',
                    unsafe_allow_html=True)
        nav = [
            ("files",       "📂", "Files"),
            ("guide",       "📖", "Study Guide"),
            ("flashcards",  "🃏", "Flashcards"),
            ("exercises",   "✏️",  "Exercises"),
            ("test",        "📝", "Test"),
            ("progress",    "📊", "Progress"),
            ("diagnostics", "🔬", "Diagnostics"),
            ("chat",        "💬", "AI Teacher Chat"),
        ]
        for key, icon, label in nav:
            prefix = "▶  " if active == key else "    "
            if st.button(f"{prefix}{icon}  {label}", key=f"sb_{key}",
                         use_container_width=True):
                st.session_state.nav_section = key
                go("class", key); st.rerun()
        st.markdown("---")
        if st.button("📓  Notebook",   key="sb_nb",   use_container_width=True):
            go("notebook"); st.rerun()
        if st.button("📚  All Courses", key="sb_dash", use_container_width=True):
            go("dashboard"); st.rerun()
        fns = course.get("file_names", [])
        if fns:
            st.markdown("---")
            st.markdown('<div class="sb-section-label">Files</div>',
                        unsafe_allow_html=True)
            for fn in fns:
                st.markdown(f'<span class="file-tag">📄 {fn}</span>',
                             unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGES
# ──────────────────────────────────────────────────────────────────────────────

def page_landing():
    st.markdown("""<div class="hero-wrap">
    <div class="hero-badge">✦ AI-Powered Learning</div>
    <div class="hero-title">Your Personal<br>AI Study Companion</div>
    <div class="hero-sub">Upload course materials. Generate study guides, flashcards,
    exercises and tests. Get AI grading and diagnostic feedback.</div>
    </div>""", unsafe_allow_html=True)

    features = [
        ("📄","Multi-PDF Upload",      "Merge documents into one knowledge base"),
        ("📖","AI Study Guides",       "Personalised summaries in your style"),
        ("🃏","Flashcards",            "Auto-generated flip cards for quick review"),
        ("✏️", "Exercises",            "MC or open-ended, Easy to Hard"),
        ("⏱️","Timed Tests",           "Auto-submit countdown with full grading"),
        ("💬","AI Teacher Chat",       "Ask questions grounded in your material"),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f'<div class="feat-pill"><div class="feat-icon">{icon}</div>'
                        f'<div class="feat-title">{title}</div>'
                        f'<div class="feat-desc">{desc}</div></div>',
                        unsafe_allow_html=True)
            st.write("")
    st.write("")
    _, mid, _ = st.columns([2,1,2])
    with mid:
        if st.button("🚀  Get Started", use_container_width=True):
            go("dashboard"); st.rerun()


def page_dashboard():
    render_top_bar("My Courses", "Select or create a course")
    courses = st.session_state.courses
    if not courses:
        st.markdown("""<div style="background:white;border-radius:16px;padding:48px 24px;
        text-align:center;box-shadow:0 1px 5px rgba(0,0,0,.06);">
        <div style="font-size:2.5rem;margin-bottom:14px;">📚</div>
        <div style="font-size:1.1rem;font-weight:700;color:#1E293B;margin-bottom:7px;">
        No courses yet</div>
        <div style="color:#64748B;font-size:.88rem;">Create your first course below.</div>
        </div>""", unsafe_allow_html=True)
        st.write("")
    else:
        for name, data in courses.items():
            fc    = len(data.get("file_names", []))
            hg    = bool(data.get("study_guide"))
            grs   = data.get("exercise_grades",[]) + data.get("test_grades",[])
            avg,_ = score_summary(grs) if grs else (None,None)
            stxt  = f"📊 {avg}/10" if avg else "📊 Not attempted"
            c1,c2 = st.columns([6,1])
            with c1:
                st.markdown(f'<div class="course-card">'
                            f'<div class="course-title">{name}</div>'
                            f'<div class="course-meta">'
                            f'{"📄 "+str(fc)+" file(s)" if fc else "📄 No files"}'
                            f' &nbsp;·&nbsp; {"✅ Guide" if hg else "⏳ No guide"}'
                            f' &nbsp;·&nbsp; {stxt}</div></div>',
                            unsafe_allow_html=True)
            with c2:
                st.write(""); st.write("")
                if st.button("Open →", key=f"open_{name}", use_container_width=True):
                    st.session_state.active_course = name
                    go("class","files"); st.rerun()
    st.write(""); st.markdown("---")
    st.markdown("**➕ Create a new course**")
    c1,c2 = st.columns([5,1])
    with c1:
        nn = st.text_input("", placeholder="e.g.  Machine Learning  /  R Programming",
                           label_visibility="collapsed", key="new_course_input")
    with c2:
        st.write("")
        if st.button("Create", use_container_width=True, key="create_btn"):
            name = nn.strip()
            if name:
                if name not in st.session_state.courses:
                    st.session_state.courses[name] = empty_course()
                st.session_state.active_course = name
                go("class","files"); st.rerun()
            else:
                st.warning("Enter a course name first.")


def page_class():
    course = get_course()
    if not course:
        st.warning("No course selected.")
        if st.button("← Back"):
            go("dashboard"); st.rerun()
        return
    render_sidebar()
    sn = st.session_state.nav_section.replace("_"," ").title()
    render_top_bar(st.session_state.active_course, f"Section — {sn}")
    s = st.session_state.nav_section
    if   s == "files":       section_files(course)
    elif s == "guide":       section_study_guide(course)
    elif s == "flashcards":  section_flashcards(course)
    elif s == "exercises":   section_exercises(course)
    elif s == "test":        section_test(course)
    elif s == "progress":    section_progress(course)
    elif s == "diagnostics": section_diagnostics(course)
    elif s == "chat":        section_chat(course)


# ── Files ─────────────────────────────────────────────────────────────────────

def section_files(course):
    st.markdown("### 📂 Course Files")
    with st.expander("❓ How document processing works"):
        st.markdown("""
**1. Text extraction** — pdfplumber reads every page of your PDFs.
**2. Chunking** — text is split into ~800-word chunks to fit the AI context window.
**3. Context selection** — top 2 chunks (~1,400 words) are sent per AI call (simplified RAG).
**Limitation:** Content beyond the first ~1,400 words may not be seen by the AI.
        """)
    uploaded = st.file_uploader("Select PDFs — hold Ctrl for multiple",
                                 type=["pdf"], accept_multiple_files=True)
    if uploaded:
        if st.button("📥  Process All Files", key="proc"):
            with st.spinner("Reading..."):
                chunks, names, wc = process_multiple_pdfs(uploaded)
            if not chunks:
                st.error("Could not extract text. Use text-based PDFs.")
            else:
                set_key("chunks",     chunks)
                set_key("file_names", names)
                for k in ("study_guide","flashcards","exercises","exercise_grades",
                          "test_questions","test_grades","diagnostic"):
                    set_key(k, [] if k in ("flashcards","exercises","exercise_grades",
                                            "test_questions","test_grades") else "")
                st.success(f"✅ {len(names)} file(s) — {wc:,} words in {len(chunks)} chunks.")
                show_pipeline_explainer(wc, len(chunks), len(names))
                st.rerun()
    fns = course.get("file_names",[])
    if fns:
        st.write("")
        for fn in fns:
            st.markdown(f'<span class="file-chip">📄 {fn}</span>', unsafe_allow_html=True)
        st.info(f"Knowledge base: **{len(course['chunks'])} chunks** ready.")
        with st.expander("Preview (first 300 words)"):
            st.write(" ".join(course["chunks"][0].split()[:300]) + "...")
    else:
        st.info("Upload PDFs above to unlock all AI features.")


# ── Study Guide ───────────────────────────────────────────────────────────────

def section_study_guide(course):
    st.markdown("### 📖 Study Guide")
    if not course.get("chunks"):
        st.warning("Upload files first."); return

    tab_gen, tab_view = st.tabs(["✨ Generate", "📄 View Guide"])

    with tab_gen:
        ca,cb,cc = st.columns(3)
        with ca: tone  = st.selectbox("Tone",   ["Simple language","Academic language"])
        with cb: depth = st.selectbox("Depth",  ["Overview","Detailed explanation"])
        with cc: fmt   = st.selectbox("Format", ["Structured headings",
                                                  "Bullet explanations",
                                                  "Paragraph explanations"])
        if st.button("✨  Generate Study Guide", key="gen_guide"):
            ctx = get_context(course["chunks"])
            with st.spinner("Writing study guide..."):
                g = generate_study_guide(ctx, tone, depth, fmt)
            if g:
                set_key("study_guide", g)
                set_key("flashcards", [])  # reset flashcards when guide regenerated
                st.success("Done! Switch to **View Guide** tab.")
                st.rerun()

    with tab_view:
        g = course.get("study_guide","")
        if g:
            st.markdown('<div class="s-card">', unsafe_allow_html=True)
            st.markdown(g)
            st.markdown('</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Download", data=g,
                file_name=f"{st.session_state.active_course}_guide.md",
                mime="text/markdown")

            st.write("")
            st.markdown("---")
            st.markdown("**🃏 Ready to make flashcards from this guide?**")
            if st.button("Generate Flashcards →", key="goto_fc"):
                st.session_state.nav_section = "flashcards"
                go("class","flashcards"); st.rerun()
        else:
            st.info("Generate a study guide first.")


# ── Flashcards ────────────────────────────────────────────────────────────────

def section_flashcards(course):
    st.markdown("### 🃏 Flashcards")
    if not course.get("study_guide"):
        st.warning("Generate a Study Guide first — flashcards are created from it.")
        return

    if st.button("✨  Generate Flashcards", key="gen_fc"):
        ctx = get_context(course["chunks"])
        with st.spinner("Creating flashcards..."):
            cards = generate_flashcards(ctx, course["study_guide"])
        if cards:
            set_key("flashcards", cards)
            st.success(f"{len(cards)} flashcards created!")
            st.rerun()
        else:
            st.error("Could not generate flashcards. Try again.")

    cards = course.get("flashcards",[])
    if not cards:
        st.info("Click above to generate flashcards from your study guide.")
        return

    st.write(f"**{len(cards)} flashcards** — click a card to flip it.")
    st.write("")

    # Track which cards are flipped
    if "fc_flipped" not in st.session_state:
        st.session_state.fc_flipped = {}
    if "fc_index" not in st.session_state:
        st.session_state.fc_index = 0

    idx = st.session_state.fc_index
    if idx >= len(cards):
        idx = 0
        st.session_state.fc_index = 0

    card    = cards[idx]
    flipped = st.session_state.fc_flipped.get(idx, False)

    # Card display
    if not flipped:
        st.markdown(f'<div class="fc-front">'
                    f'<div class="fc-label">CONCEPT / QUESTION</div>'
                    f'<div class="fc-text">{card["front"]}</div>'
                    f'</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="fc-back">'
                    f'<div class="fc-label" style="color:#6366F1;">ANSWER / EXPLANATION</div>'
                    f'<div class="fc-text">{card["back"]}</div>'
                    f'</div>', unsafe_allow_html=True)

    st.write("")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if st.button("🔄 Flip", use_container_width=True, key="fc_flip"):
            st.session_state.fc_flipped[idx] = not flipped
            st.rerun()
    with c2:
        if st.button("◀ Prev", use_container_width=True, key="fc_prev"):
            st.session_state.fc_index = max(0, idx - 1)
            st.session_state.fc_flipped = {}
            st.rerun()
    with c3:
        if st.button("Next ▶", use_container_width=True, key="fc_next"):
            st.session_state.fc_index = min(len(cards)-1, idx + 1)
            st.session_state.fc_flipped = {}
            st.rerun()
    with c4:
        if st.button("🔀 Shuffle", use_container_width=True, key="fc_shuffle"):
            random.shuffle(cards)
            set_key("flashcards", cards)
            st.session_state.fc_index   = 0
            st.session_state.fc_flipped = {}
            st.rerun()

    st.write("")
    st.markdown(f'<div style="text-align:center;color:#94A3B8;font-size:.8rem;">'
                f'Card {idx+1} of {len(cards)}</div>', unsafe_allow_html=True)

    # Progress dots
    dots = ""
    for i in range(len(cards)):
        color = "#6366F1" if i == idx else "#E2E8F0"
        dots += f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};margin:2px;"></span>'
    st.markdown(f'<div style="text-align:center;margin-top:6px;">{dots}</div>',
                unsafe_allow_html=True)


# ── Exercises ─────────────────────────────────────────────────────────────────

def section_exercises(course):
    st.markdown("### ✏️ Practice Exercises")
    if not course.get("chunks"):
        st.warning("Upload files first."); return

    c1,c2,c3 = st.columns(3)
    with c1:
        q_type = st.selectbox("Question Type",
                               ["Multiple Choice","Open-ended"],
                               key="ex_type")
    with c2:
        difficulty = st.selectbox("Difficulty",
                                   ["Easy","Medium","Hard"],
                                   key="ex_diff")
    with c3:
        st.write("")
        diff_colors = {"Easy":"diff-easy","Medium":"diff-medium","Hard":"diff-hard"}
        st.markdown(f'<br><span class="{diff_colors[difficulty]}">{difficulty}</span>',
                    unsafe_allow_html=True)

    if st.button("🔄  Generate Questions", key="gen_ex"):
        ctx = get_context(course["chunks"])
        with st.spinner("Generating questions..."):
            if q_type == "Multiple Choice":
                qs = generate_mc_questions(ctx, difficulty, count=6)
            else:
                qs = generate_open_questions(ctx, difficulty, count=6)
        if qs:
            set_key("exercises",       qs)
            set_key("exercise_answers",{})
            set_key("exercise_grades", [])
            set_key("ex_q_type",       q_type)
            set_key("ex_difficulty",   difficulty)
            st.success(f"{len(qs)} {q_type} questions generated!")
            st.rerun()
        else:
            st.error("Could not generate questions. Try again.")

    exercises = course.get("exercises",[])
    if not exercises:
        st.info("Click above to generate questions.")
        return

    stored_type = course.get("ex_q_type", "Open-ended")
    answers     = course.get("exercise_answers", {})

    st.write(f"**{len(exercises)} {stored_type} questions:**")
    st.write("")

    for i, q in enumerate(exercises):
        st.markdown(f'<div class="q-card"><div class="q-num">Question {i+1}</div>'
                    f'<div class="q-text">{q.get("question","")}</div></div>',
                    unsafe_allow_html=True)

        if stored_type == "Multiple Choice":
            opts  = q.get("options",{})
            radio = st.radio(
                "Choose:",
                options=list(opts.keys()),
                format_func=lambda k, o=opts: f"{k}: {o[k]}",
                key=f"ex_mc_{i}",
                index=None,
            )
            answers[i] = radio
        else:
            ans = st.text_area("", key=f"ex_oe_{i}",
                               value=answers.get(i,""),
                               height=80,
                               placeholder="Type your answer here...",
                               label_visibility="collapsed")
            answers[i] = ans
        st.write("")

    set_key("exercise_answers", answers)

    if st.button("📊  Submit for Grading", key="grade_ex", use_container_width=True):
        ctx    = get_context(course["chunks"])
        grades = []
        bar    = st.progress(0, text="Grading...")
        for i, q in enumerate(exercises):
            bar.progress((i+1)/len(exercises), text=f"Grading {i+1}/{len(exercises)}...")
            if stored_type == "Multiple Choice":
                g = grade_mc(q, answers.get(i,""))
            else:
                g = grade_open(ctx, q, answers.get(i,""))
            grades.append(g)
        bar.empty()
        set_key("exercise_grades", grades)
        st.success("Graded!"); st.rerun()

    grades = course.get("exercise_grades",[])
    if not grades:
        return

    st.write("")
    st.markdown("**Results:**")
    avg, cat = score_summary(grades)
    m1,m2    = st.columns(2)
    m1.metric("Average Score", f"{avg} / 10")
    m2.metric("Level", cat)

    show_accuracy_disclaimer()
    st.write("")

    for i, g in enumerate(grades, 1):
        with st.expander(f"Q{i} — {g['score']}/10"):
            st.markdown(f"**Question:** {g['question']}")
            if stored_type == "Multiple Choice":
                opts = g.get("options",{})
                for letter, text in opts.items():
                    if letter == g.get("correct"):
                        st.markdown(f'<div class="mc-correct">✅ {letter}: {text} (Correct)</div>',
                                    unsafe_allow_html=True)
                    elif letter == g.get("student") and not g.get("is_correct"):
                        st.markdown(f'<div class="mc-wrong">❌ {letter}: {text} (Your answer)</div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="mc-neutral">{letter}: {text}</div>',
                                    unsafe_allow_html=True)
                st.markdown(f"**Explanation:** {g.get('explanation','')}")
            else:
                st.markdown(f"**Your Answer:** {g.get('answer','')}")
                st.markdown(f"✅ **Strengths:** {g.get('strengths','')}")
                st.markdown(f"⚠️ **Weaknesses:** {g.get('weaknesses','')}")
                st.markdown(f"📌 **Revision focus:** {g.get('revision','')}")


# ── Test ──────────────────────────────────────────────────────────────────────

def section_test(course):
    st.markdown("### 📝 Mini Test")
    if not course.get("chunks"):
        st.warning("Upload files first."); return

    test_qs    = course.get("test_questions",[])
    submitted  = course.get("test_submitted", False)
    start_time = course.get("test_start_time", None)

    # ── Setup (no test yet or already submitted) ──────────────────────────────
    if not test_qs or submitted:
        if submitted:
            st.success("Test already submitted. Scroll down for results, or generate a new test.")

        c1,c2,c3 = st.columns(3)
        with c1:
            q_type = st.selectbox("Question Type",
                                   ["Multiple Choice","Open-ended"],
                                   key="test_type")
        with c2:
            difficulty = st.selectbox("Difficulty",
                                       ["Easy","Medium","Hard"],
                                       key="test_diff")
        with c3:
            mins = TIMER_DURATIONS[difficulty] * 5
            st.info(f"⏱️ Timer: **{mins} minutes**")

        if st.button("🎯  Generate Test", key="gen_test"):
            ctx = get_context(course["chunks"])
            with st.spinner("Creating exam..."):
                if q_type == "Multiple Choice":
                    qs = generate_mc_questions(ctx, difficulty, count=5)
                else:
                    qs = generate_open_questions(ctx, difficulty, count=5, is_test=True)
            if qs:
                set_key("test_questions",  qs)
                set_key("test_answers",    {})
                set_key("test_grades",     [])
                set_key("test_q_type",     q_type)
                set_key("test_difficulty", difficulty)
                set_key("test_start_time", time.time())
                set_key("test_submitted",  False)
                st.rerun()
            else:
                st.error("Could not generate test. Try again.")

        grades = course.get("test_grades",[])
        if grades:
            st.write("")
            st.markdown("**Last test results:**")
            avg, cat = score_summary(grades)
            m1,m2    = st.columns(2)
            m1.metric("Score", f"{avg} / 10")
            m2.metric("Result", cat)
            stored_type = course.get("test_q_type","Open-ended")
            for i, g in enumerate(grades, 1):
                with st.expander(f"Q{i} — {g['score']}/10"):
                    st.markdown(f"**Question:** {g['question']}")
                    if stored_type == "Multiple Choice":
                        opts = g.get("options",{})
                        for letter, text in opts.items():
                            if letter == g.get("correct"):
                                st.markdown(f'<div class="mc-correct">✅ {letter}: {text}</div>',
                                            unsafe_allow_html=True)
                            elif letter == g.get("student") and not g.get("is_correct"):
                                st.markdown(f'<div class="mc-wrong">❌ {letter}: {text}</div>',
                                            unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="mc-neutral">{letter}: {text}</div>',
                                            unsafe_allow_html=True)
                        st.markdown(f"**Explanation:** {g.get('explanation','')}")
                    else:
                        st.markdown(f"**Answer:** {g.get('answer','')}")
                        st.markdown(f"✅ **Strengths:** {g.get('strengths','')}")
                        st.markdown(f"⚠️ **Weaknesses:** {g.get('weaknesses','')}")
        return

    # ── Active test ───────────────────────────────────────────────────────────
    difficulty  = course.get("test_difficulty","Medium")
    stored_type = course.get("test_q_type","Open-ended")
    total_mins  = TIMER_DURATIONS[difficulty] * len(test_qs)
    elapsed     = time.time() - (start_time or time.time())
    remaining   = max(0, total_mins * 60 - elapsed)
    mins_left   = int(remaining // 60)
    secs_left   = int(remaining % 60)
    time_up     = remaining <= 0

    # Timer display
    timer_str = f"⏱️  {mins_left:02d}:{secs_left:02d}"
    if remaining > total_mins * 60 * 0.5:
        timer_class = "timer-ok"
    elif remaining > total_mins * 60 * 0.2:
        timer_class = "timer-warn"
    else:
        timer_class = "timer-danger"

    tc, _, tb = st.columns([2,3,2])
    with tc:
        st.markdown(f'<div class="{timer_class}">{timer_str}</div>',
                    unsafe_allow_html=True)
    with tb:
        if st.button("🔄 Refresh Timer", key="refresh_timer"):
            st.rerun()

    if time_up:
        st.warning("⏰ Time is up! Your answers are being submitted automatically.")

    st.markdown(f'<div style="background:#1E293B;border-radius:12px;padding:14px 22px;margin:16px 0;">'
                f'<div style="color:white;font-weight:700;">📋 Exam — {len(test_qs)} Questions'
                f' | {stored_type} | {difficulty}</div>'
                f'<div style="color:#94A3B8;font-size:.82rem;margin-top:3px;">'
                f'Answer all questions before time runs out.</div></div>',
                unsafe_allow_html=True)

    answers    = course.get("test_answers",{})
    type_labels = ["Conceptual","Conceptual","Applied","Analysis","Integrative"]
    type_colors = ["#6366F1","#6366F1","#10B981","#F59E0B","#7C3AED"]

    for i, q in enumerate(test_qs):
        label = type_labels[i] if i < len(type_labels) else "Question"
        color = type_colors[i] if i < len(type_colors) else "#6366F1"
        st.markdown(f'<div class="q-card" style="border-left:4px solid {color};">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:9px;">'
                    f'<span class="q-num">Question {i+1}</span>'
                    f'<span style="background:{color}22;color:{color};padding:2px 10px;'
                    f'border-radius:10px;font-size:.72rem;font-weight:700;">{label}</span></div>'
                    f'<div class="q-text">{q.get("question","")}</div></div>',
                    unsafe_allow_html=True)

        if stored_type == "Multiple Choice":
            opts  = q.get("options",{})
            radio = st.radio("", options=list(opts.keys()),
                             format_func=lambda k, o=opts: f"{k}: {o[k]}",
                             key=f"test_mc_{i}", index=None)
            answers[i] = radio
        else:
            ans = st.text_area("", key=f"test_oe_{i}",
                               value=answers.get(i,""),
                               height=100,
                               placeholder="Write your exam answer...",
                               label_visibility="collapsed")
            answers[i] = ans
        st.write("")

    set_key("test_answers", answers)

    do_submit = time_up
    if st.button("📤  Submit Test", key="submit_test", use_container_width=True):
        do_submit = True

    if do_submit:
        ctx    = get_context(course["chunks"])
        grades = []
        bar    = st.progress(0, text="Grading test...")
        for i, q in enumerate(test_qs):
            bar.progress((i+1)/len(test_qs), text=f"Grading {i+1}/{len(test_qs)}...")
            if stored_type == "Multiple Choice":
                g = grade_mc(q, answers.get(i,""))
            else:
                g = grade_open(ctx, q, answers.get(i,""))
            grades.append(g)
        bar.empty()
        set_key("test_grades",   grades)
        set_key("test_submitted", True)
        st.success("Test submitted and graded!")
        st.rerun()


# ── Progress ──────────────────────────────────────────────────────────────────

def section_progress(course):
    st.markdown("### 📊 Progress Overview")
    st.write("")
    ex_g  = course.get("exercise_grades",[])
    te_g  = course.get("test_grades",[])
    all_g = ex_g + te_g
    if not all_g:
        st.info("Complete exercises or the test to see progress here.")
        return
    ea,ec = score_summary(ex_g) if ex_g else (0,"—")
    ta,tc = score_summary(te_g) if te_g else (0,"—")
    oa,oc = score_summary(all_g)
    c1,c2,c3 = st.columns(3)
    for col,val,lbl,cat in [(c1,ea,"Exercises",ec),(c2,ta,"Test",tc),(c3,oa,"Overall",oc)]:
        with col:
            st.markdown(f'<div class="m-card"><div class="m-value">{val}/10</div>'
                        f'<div class="m-label">{lbl}</div>'
                        f'<div class="m-cat">{cat}</div></div>',
                        unsafe_allow_html=True)
    st.write("")
    st.markdown("**Score per question:**")
    st.write("")

    if all_g:
        import pandas as pd
        cd = {}
        for i,g in enumerate(ex_g, 1):
            cd[f"Ex Q{i}"] = g["score"]
        for i,g in enumerate(te_g, 1):
            cd[f"Test Q{i}"] = g["score"]
        df = pd.DataFrame({"Q":list(cd.keys()),"Score":list(cd.values())}).set_index("Q")
        st.bar_chart(df, height=260)

        st.write("")
        for i,g in enumerate(all_g,1):
            pct   = g["score"]*10
            color = "#10B981" if g["score"]>=7 else "#F59E0B" if g["score"]>=5 else "#F43F5E"
            src   = "Exercise" if i<=len(ex_g) else "Test"
            st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
                        f'<div style="width:90px;font-size:.78rem;color:#64748B;">{src} Q{i}</div>'
                        f'<div style="flex:1;">{progress_bar_html(pct,color)}</div>'
                        f'<div style="width:38px;font-size:.82rem;font-weight:700;'
                        f'color:{color};text-align:right;">{g["score"]}/10</div></div>',
                        unsafe_allow_html=True)

    st.write("")
    st.markdown("**Checklist:**")
    checks = [
        ("📄 Files uploaded",        bool(course.get("file_names"))),
        ("📖 Study guide generated", bool(course.get("study_guide"))),
        ("🃏 Flashcards created",    bool(course.get("flashcards"))),
        ("✏️ Exercises done",         bool(ex_g)),
        ("📝 Test completed",         bool(te_g)),
        ("🔬 Diagnostic generated",   bool(course.get("diagnostic"))),
        ("📓 Notes written",          any(s.get("content","").strip()
                                         for s in course.get("notebook_sessions",[])
                                         if s.get("id","").startswith("user"))),
    ]
    for label,done in checks:
        st.markdown(f"{'✅' if done else '⬜'} {label}")


# ── Diagnostics ───────────────────────────────────────────────────────────────

def section_diagnostics(course):
    st.markdown("### 🔬 AI Diagnostic Report")
    all_g = course.get("exercise_grades",[]) + course.get("test_grades",[])
    if not all_g:
        st.info("Complete exercises or the test first."); return
    avg,cat = score_summary(all_g)
    st.metric("Overall", f"{avg}/10 — {cat}")
    st.write("")
    if st.button("🧠  Generate Diagnostic", key="gen_diag"):
        ctx   = get_context(course.get("chunks",[]))
        qtype = course.get("test_q_type") or course.get("ex_q_type","Open-ended")
        with st.spinner("Analysing performance..."):
            r = generate_diagnostic(ctx, all_g, qtype)
        if r:
            set_key("diagnostic", r); st.rerun()
    d = course.get("diagnostic","")
    if d:
        st.markdown('<div class="s-card">', unsafe_allow_html=True)
        st.markdown(d)
        st.markdown('</div>', unsafe_allow_html=True)
        st.download_button("⬇️ Download", data=d,
            file_name=f"{st.session_state.active_course}_diagnostic.md",
            mime="text/markdown")


# ── Teacher Chat ──────────────────────────────────────────────────────────────

def section_chat(course):
    st.markdown("### 💬 AI Teacher Chat")
    if not course.get("chunks"):
        st.warning("Upload files first — the AI teacher answers based on your material."); return

    tab_general, tab_context = st.tabs(["🎓 General Chat", "🔍 Ask About Specific Text"])

    # ── General Chat ──────────────────────────────────────────────────────────
    with tab_general:
        st.write("Ask the AI teacher any question about your course material.")
        st.write("")

        msgs = st.session_state.global_chat
        if msgs:
            for m in msgs:
                cls = "chat-user" if m["role"]=="user" else "chat-ai"
                st.markdown(f'<div class="{cls}">{m["content"]}</div>',
                            unsafe_allow_html=True)
            st.write("")

        user_input = st.text_input("Ask a question...",
                                    key="chat_input",
                                    placeholder="e.g. Can you explain what the pipe operator does?")

        c1,c2 = st.columns([4,1])
        with c1:
            send = st.button("Send →", key="chat_send", use_container_width=True)
        with c2:
            if st.button("Clear", key="chat_clear"):
                st.session_state.global_chat = []; st.rerun()

        if send and user_input.strip():
            st.session_state.global_chat.append(
                {"role":"user","content":user_input.strip()})
            ctx = get_context(course["chunks"])
            with st.spinner("AI Teacher is thinking..."):
                reply = chat_with_teacher(ctx, st.session_state.global_chat)
            if reply:
                st.session_state.global_chat.append(
                    {"role":"assistant","content":reply})
            st.rerun()

    # ── Contextual Chat ───────────────────────────────────────────────────────
    with tab_context:
        st.write("Paste a specific sentence, concept, or question you want explained.")
        st.markdown("""
        **How to use:** Copy any text from your study guide, an exercise question,
        or your notes — paste it in the box below, then ask your question about it.
        """)
        st.write("")

        highlight = st.text_area("📌 Paste the text you want to ask about:",
                                  key="ctx_highlight",
                                  height=80,
                                  placeholder='e.g. "across(where(is.logical), ~ as.numeric(.x))"')

        ctx_msgs = st.session_state.context_chat

        if highlight.strip() and ctx_msgs:
            st.markdown(f'<div style="background:#EEF2FF;border:1px solid #C7D2FE;'
                        f'border-radius:8px;padding:10px 14px;margin-bottom:12px;'
                        f'font-size:.82rem;color:#3730A3;">'
                        f'📌 Asking about: <em>"{highlight[:100]}..."</em></div>',
                        unsafe_allow_html=True)
            for m in ctx_msgs:
                cls = "chat-user" if m["role"]=="user" else "chat-ai"
                st.markdown(f'<div class="{cls}">{m["content"]}</div>',
                             unsafe_allow_html=True)
            st.write("")

        ctx_q = st.text_input("Your question about the highlighted text:",
                               key="ctx_question",
                               placeholder="What does .x mean in this context?")

        c1,c2 = st.columns([4,1])
        with c1:
            ctx_send = st.button("Ask →", key="ctx_send", use_container_width=True)
        with c2:
            if st.button("Clear", key="ctx_clear"):
                st.session_state.context_chat = []; st.rerun()

        if ctx_send and ctx_q.strip() and highlight.strip():
            st.session_state.context_chat.append(
                {"role":"user","content":ctx_q.strip()})
            ctx = get_context(course["chunks"])
            with st.spinner("Explaining..."):
                reply = contextual_chat(ctx, highlight.strip(),
                                         st.session_state.context_chat)
            if reply:
                st.session_state.context_chat.append(
                    {"role":"assistant","content":reply})
            st.rerun()
        elif ctx_send and not highlight.strip():
            st.warning("Paste the text you want to ask about first.")


# ── Notebook ──────────────────────────────────────────────────────────────────

def page_notebook():
    course = get_course()
    if not course:
        st.warning("No course selected.")
        if st.button("← Back"):
            go("dashboard"); st.rerun()
        return

    render_sidebar()
    render_top_bar(st.session_state.active_course, "Study Notebook")

    st.markdown("""<div style="background:#1E293B;border-radius:12px;padding:14px 22px;
    margin-bottom:22px;">
    <div style="color:white;font-weight:700;font-size:.95rem;">📓 Study Notebook</div>
    <div style="color:#94A3B8;font-size:.82rem;margin-top:3px;">
    Organised study sessions · Study guide on the right · Personal notes on the left
    </div></div>""", unsafe_allow_html=True)

    sessions = course.get("notebook_sessions", [])

    # ── Left: session list + editor ───────────────────────────────────────────
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("##### 📋 Sessions")

        # Add new session button
        if st.button("➕  New Session", use_container_width=True, key="new_session"):
            today      = date.today().isoformat()
            session_n  = len([s for s in sessions if s.get("id","").startswith("user")]) + 1
            new_s = {
                "id":      f"user_{int(time.time())}",
                "date":    today,
                "title":   f"Session {session_n} — {today}",
                "content": "",
            }
            sessions.append(new_s)
            set_key("notebook_sessions", sessions)
            set_key("active_nb_session", new_s["id"])
            st.rerun()

        st.write("")

        # Session list
        for s in reversed(sessions):
            is_example = s.get("id","").startswith("ex")
            tag = " 📌" if is_example else ""
            c1,c2 = st.columns([5,1])
            with c1:
                st.markdown(f'<div class="nb-session-card">'
                            f'<div class="nb-session-date">{s.get("date","")}{tag}</div>'
                            f'<div class="nb-session-title">{s.get("title","")}</div>'
                            f'</div>', unsafe_allow_html=True)
            with c2:
                st.write("")
                if st.button("Edit", key=f"edit_{s['id']}", use_container_width=True):
                    set_key("active_nb_session", s["id"])
                    st.rerun()

        # Editor for active session
        active_id = course.get("active_nb_session")
        active_s  = next((s for s in sessions if s["id"]==active_id), None)

        if active_s:
            st.write("")
            st.markdown(f"**Editing: {active_s['title']}**")

            new_title = st.text_input("Session title:",
                                       value=active_s.get("title",""),
                                       key=f"title_{active_id}")

            new_content = st.text_area("Notes:",
                                        value=active_s.get("content",""),
                                        height=280,
                                        key=f"content_{active_id}",
                                        placeholder="Write your notes here...")

            if st.button("💾  Save", use_container_width=True, key="save_nb"):
                for s in sessions:
                    if s["id"] == active_id:
                        s["title"]   = new_title
                        s["content"] = new_content
                        break
                set_key("notebook_sessions", sessions)
                st.success("Saved!")

            wc = len(new_content.split()) if new_content.strip() else 0
            st.caption(f"{wc} words")
        else:
            st.info("Click **Edit** on a session above, or create a new one.")

    # ── Right: Study Guide viewer ─────────────────────────────────────────────
    with right:
        st.markdown("##### 📖 Study Guide Reference")
        guide = course.get("study_guide","")
        if guide:
            with st.container():
                st.markdown(guide)
        else:
            st.markdown("""<div style="background:white;border-radius:12px;padding:40px 24px;
            text-align:center;color:#94A3B8;min-height:250px;">
            <div style="font-size:2rem;margin-bottom:12px;">📖</div>
            <div style="font-weight:600;color:#475569;">No study guide yet</div>
            <div style="font-size:.82rem;margin-top:7px;">
            Generate one in the Study Guide section first.</div></div>""",
            unsafe_allow_html=True)
            if st.button("📖  Generate Study Guide", use_container_width=True):
                go("class","guide"); st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="AI Learning Companion",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="auto",
    )
    inject_css()
    init_session_state()

    p = st.session_state.page
    if   p == "landing":   page_landing()
    elif p == "dashboard": page_dashboard()
    elif p == "class":     page_class()
    elif p == "notebook":  page_notebook()
    else:                  page_landing()


if __name__ == "__main__":
    main()
