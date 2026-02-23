# Adaptive AI Learning Companion

An AI-powered student workspace that transforms uploaded course materials 
into a personalised learning environment.

## What It Does

Upload any course PDF and the AI will:
1. Generate a personalised **Study Guide** (your tone, depth, and format)
2. Create **Practice Exercises** — 7 open-ended questions
3. Simulate a **Mini Test** with conceptual, applied, and integrative questions
4. **Grade your answers** against the source material
5. Generate a **Diagnostic Report** identifying knowledge gaps

All AI outputs are grounded strictly in the uploaded document.

## Tech Stack

- **Frontend:** Streamlit
- **AI Engine:** Google Gemini API (gemini-2.0-flash-lite)
- **PDF Processing:** pdfplumber
- **Language:** Python 3.11

## How to Run Locally

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file and add: `GEMINI_API_KEY=your-key-here`
6. Run: `streamlit run app.py`

## Architecture
```
PDF Upload → Text Extraction (pdfplumber) → Chunking (~800 words/chunk)
→ Context Selection (top 2 chunks) → Gemini API → Structured Output
→ Session State Storage → Streamlit UI
```

This is a simplified form of Retrieval-Augmented Generation (RAG).

## Project Structure

- `app.py` — complete single-file Streamlit application
- `requirements.txt` — Python dependencies
- `.env` — API key (not committed to GitHub)
- `.gitignore` — excludes sensitive files

## Academic Context

Built as a university prototyping assignment demonstrating AI-centered 
product design, prompt engineering, and adaptive feedback systems.