# AI Resume Analyzer Agent (Local LLM – Ollama)

AI Resume Analyzer Agent is a command-line application built using a locally deployed Large Language Model (LLM) via Ollama. The system analyzes resume text and generates structured JSON output containing skills, role suggestions, strengths, gaps, improvement plans, and ATS optimization tips.

This project demonstrates practical GenAI engineering concepts including prompt design, structured output enforcement, JSON validation, regex-based parsing, and robust LLM response handling.

---

## Project Overview

The application accepts raw resume text from the user and performs structured analysis using a local LLM. The output is returned in machine-readable JSON format to ensure consistency and reliability.

The system is designed to handle common LLM formatting inconsistencies by extracting and validating JSON responses safely before parsing.

---

## Key Features

- Local LLM deployment using Ollama (no external API keys required)
- Structured JSON output generation
- Prompt engineering for analytical reasoning
- Regex-based JSON extraction to handle LLM formatting variations
- Safe JSON parsing with error handling
- Configurable generation parameters (temperature, token limits)
- Modular project structure

---

## Project Structure

ai-resume-analyzer-agent/

main.py          - CLI interface and formatted output  
analyzer.py      - LLM interaction and structured JSON enforcement  
config.py        - Model configuration and generation parameters  
requirements.txt  
README.md  
.gitignore  

---

## Tech Stack

- Python
- Ollama (Local LLM Runtime)
- Llama3 or Mistral model
- JSON parsing
- Regex-based validation

---

## Installation

1. Install Ollama  
Download from:  
https://ollama.com/download  

Verify installation:

ollama --version  

2. Pull the model:

ollama pull llama3  

(or use mistral if preferred)

3. Install Python dependencies:

pip install -r requirements.txt  

---

## Run the Application

python main.py  

Paste your resume text.  
When finished, type:

END  

The system will analyze the resume and return structured JSON output.

---

## Output Format

The application returns structured JSON in the following format:

{
  "skills": [],
  "roles": [],
  "strengths": [],
  "gaps": [],
  "improvement_plan": [],
  "ats_tips": []
}

Each field contains a list of concise strings to ensure machine-readable and automation-ready output.

---

## Engineering Considerations

- Local LLM deployment demonstrates understanding of model runtime management without relying on cloud APIs.
- Strict JSON output enforcement ensures structured results.
- Regex extraction is used to handle cases where the LLM includes extra text outside JSON.
- Temperature tuning balances reasoning depth and output consistency.
- Modular architecture separates configuration, logic, and interface layers.

---

## Possible Extensions

- Resume scoring system (0–100 evaluation)
- PDF resume upload support
- FastAPI backend version
- Web-based interface
- Multi-resume comparison system

---

## Author

Sai Madhava  
Computer Science and Artificial Intelligence  
Backend and GenAI-focused engineering projects

---

## License

For educational and demonstration purposes.
