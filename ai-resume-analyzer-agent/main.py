# main.py
# CLI interface for AI Resume Analyzer.
# Preserved: original paste-text workflow.
# Added: --file argument for PDF/DOCX input.

from analyzer import analyze_resume
from text_preprocessor import preprocess_resume_text
from nlp_engine import analyze_resume_nlp
import json
import argparse
import sys
import os


def analyze_from_text(resume_text: str) -> None:
    """Run analysis on raw text input and print results."""
    if not resume_text.strip():
        print("No resume text provided.")
        return

    # Preprocess
    cleaned = preprocess_resume_text(resume_text)
    print(f"\n[Preprocessed: {len(resume_text)} → {len(cleaned)} characters]\n")

    # NLP analysis
    print("Running NLP analysis...")
    nlp_results = analyze_resume_nlp(cleaned)

    # Print NLP skill extraction
    skills = nlp_results["skills"]
    if skills["all_skills"]:
        print(f"\n=== Skills Detected (NLP) [{len(skills['all_skills'])} skills] ===")
        for category, skill_list in skills["categorized"].items():
            print(f"  {category}: {', '.join(skill_list)}")

    # Print similarity score
    sim = nlp_results["similarity"]
    if sim["score"] is not None:
        print(f"\n=== Keyword Relevance Score: {sim['percentage']} ===")
        print(f"  Method: {sim['method']}")

    # LLM analysis
    print("\nRunning Ollama/Llama 3 analysis...")
    llm_result = analyze_resume(cleaned)

    print("\n=== LLM Structured Analysis ===\n")
    print(json.dumps(llm_result, indent=4))

    # Combined output
    combined = {
        "llm_analysis": llm_result,
        "nlp_analysis": {
            "skills_detected": skills,
            "tfidf_keywords": nlp_results["tfidf_keywords"],
            "similarity_score": nlp_results["similarity"],
        },
    }

    print("\n=== Full Combined Analysis ===\n")
    print(json.dumps(combined, indent=4))


def analyze_from_file(file_path: str) -> None:
    """Extract text from a file and run analysis."""
    from document_parser import extract_text

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in (".pdf", ".docx"):
        print(f"Error: Unsupported file type '{ext}'. Use PDF or DOCX.")
        sys.exit(1)

    print(f"Extracting text from: {file_path}")
    try:
        raw_text = extract_text(file_path)
        print(f"Extracted {len(raw_text)} characters from {ext.upper()} file.\n")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    analyze_from_text(raw_text)


def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Analyzer — Analyze resumes using Ollama/Llama 3"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Path to a resume file (PDF or DOCX) to analyze",
    )
    args = parser.parse_args()

    if args.file:
        analyze_from_file(args.file)
    else:
        # Original CLI workflow — paste text and type END
        print("=== AI Resume Analyzer Agent ===\n")
        print("Paste your resume text below.")
        print("When finished, type END on a new line.\n")

        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)

        resume_text = "\n".join(lines)
        analyze_from_text(resume_text)


if __name__ == "__main__":
    main()