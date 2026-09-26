# AI Resume Analyzer — Upgraded Edition

**AI Resume Analyzer** is an intelligent resume parsing, evaluation, and feedback system powered by a local Large Language Model (**Ollama / Llama 3**) and lightweight **NLP / ML techniques**.

It provides a modern **Web Dashboard** for file uploads (PDF & DOCX) alongside a fully preserved **CLI Workflow** for raw text and file analysis.

---

## Architecture & Workflow

```
[ PDF / DOCX File ]  or  [ Raw Resume Text ]
         │                       │
         ▼                       ▼
 ┌───────────────┐       ┌───────────────┐
 │ Document      │       │ CLI Input /   │
 │ Parser        │       │ Direct Text   │
 └───────┬───────┘       └───────┬───────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │ Text Preprocessing &  │
         │ Normalization         │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │ Resume Analysis Engine│
         ├───────────────────────┤
         │  • NLP/ML (TF-IDF,    │
         │    Skill Extraction,  │
         │    Cosine Similarity) │
         │  • Ollama / Llama 3   │
         │    (Structured JSON)  │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │ Web Results Dashboard │
         │  / CLI JSON Output    │
         └───────────────────────┘
```

---

## Key Features

- **Web Dashboard**: Clean, responsive, dark-mode interface built with Flask, Vanilla CSS, and modern JS. Features drag-and-drop file upload, file validation, real-time processing indicators, and interactive result visualization.
- **Document Parsing**: Robust text extraction from `.pdf` (via PyMuPDF) and `.docx` (via python-docx) files with graceful handling of empty documents, scanned/image-only PDFs, and file corruption.
- **Text Preprocessing**: Information-preserving normalization pipeline that fixes encoding artifacts, normalizes whitespace, cleans extraction noise, and standardizes bullet points without destroying structure.
- **NLP & Lightweight ML**:
  - **Skill Extraction**: Regex pattern matching against a curated vocabulary of 150+ technical skills categorized into 6 domains, complemented by optional spaCy NER entity detection.
  - **TF-IDF Keyword Analysis**: Computes document term frequencies against generic resume benchmarks to highlight distinctive keywords.
  - **Cosine Similarity Scoring**: Quantifies structural keyword alignment against standard software engineering profiles with transparent calculation disclosures.
- **Enhanced LLM Analyzer**:
  - Deep evaluation covering Profile Summary, Strengths, Weaknesses, Categorized Skills, Experience Depth, Projects Impact, Education, Certifications, Actionable Improvements, ATS Observations, and Suggested Future Roles.
  - Multi-step JSON extraction and error recovery to guarantee valid output formatting.
- **Preserved CLI**: Full CLI support for both direct text input (`python main.py`) and file input (`python main.py --file resume.pdf`).

---

## Project Structure

```text
ai-resume-analyzer-agent/
├── app.py                # Flask web server & API endpoints
├── document_parser.py    # PDF (PyMuPDF) and DOCX (python-docx) text extraction
├── text_preprocessor.py  # Text normalization and artifact cleaning
├── nlp_engine.py         # Skill extraction, TF-IDF analysis & cosine similarity
├── analyzer.py          # Ollama / Llama 3 prompt engineering & JSON validation
├── config.py            # Global settings & environment configurations
├── main.py              # Extended CLI interface (supports --file and raw text)
├── requirements.txt     # Python dependencies
├── static/
│   ├── app.js           # Frontend interactive logic
│   └── style.css        # Dashboard styling (dark theme & micro-animations)
└── templates/
    └── index.html       # Web application UI template
```

---

## Tech Stack

- **Backend**: Python 3.10+, Flask
- **LLM Runtime**: Ollama (Llama 3 / Mistral)
- **Document Extraction**: PyMuPDF (`fitz`), `python-docx`
- **NLP / ML**: `scikit-learn` (TF-IDF, Cosine Similarity), `spacy`, Regex
- **Frontend**: HTML5, Vanilla CSS3 (Custom Variables, CSS Grid/Flexbox), JavaScript (ES6+)

---

## Installation & Setup

### 1. Install Ollama & Pull Model

Download Ollama from [ollama.com](https://ollama.com/download), verify installation, and pull your target model:

```bash
ollama --version
ollama pull llama3
```

Ensure the Ollama server is running (`ollama serve`).

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

*(Optional)* Download the spaCy small English model for expanded entity recognition:

```bash
python -m spacy download en_core_web_sm
```

---

## Running the Application

### Option A: Web Interface (Recommended)

Launch the Flask web server:

```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5000`. Drag & drop a PDF or DOCX resume to view the interactive dashboard.

### Option B: Command Line Interface (CLI)

**File Mode (PDF / DOCX):**

```bash
python main.py --file path/to/resume.pdf
```

**Interactive Paste Mode:**

```bash
python main.py
```

Paste your resume text into the terminal, then type `END` on a new line.

---

## Output JSON Schema

The analyzer returns a structured JSON payload:

```json
{
  "summary": "Concise profile description...",
  "strengths": ["Item 1", "Item 2"],
  "weaknesses": ["Item 1", "Item 2"],
  "skills": {
    "programming_languages": [],
    "frameworks_libraries": [],
    "databases": [],
    "cloud_devops": [],
    "ai_ml": [],
    "tools": [],
    "other": []
  },
  "experience_analysis": {
    "relevance": "...",
    "clarity": "...",
    "impact": "...",
    "technical_depth": "...",
    "measurable_achievements": "..."
  },
  "projects_analysis": {
    "technical_relevance": "...",
    "technologies_used": [],
    "clarity": "...",
    "measurable_impact": "...",
    "engineering_ability": "..."
  },
  "education": "...",
  "certifications": [],
  "improvement_suggestions": [],
  "ats_observations": [],
  "suggested_roles": []
}
```

---

## Author & License

- **Author**: Sai Madhava
- **Focus**: AI Engineering, NLP & Full-Stack Systems
- **License**: Educational & Demonstration Purposes