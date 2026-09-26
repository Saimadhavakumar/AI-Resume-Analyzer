# app.py
# Flask web server for AI Resume Analyzer.
# Provides file upload, analysis, and results dashboard.

import os
import json
import time
from flask import Flask, request, jsonify, render_template, send_from_directory
from config import (
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG,
    MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS,
)
from document_parser import extract_text_from_bytes
from text_preprocessor import preprocess_resume_text
from analyzer import analyze_resume
from nlp_engine import analyze_resume_nlp

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_BYTES


@app.route("/")
def index():
    """Serve the main web UI."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    API endpoint: Upload a resume file and receive structured analysis.

    Expects: multipart/form-data with a 'file' field containing a PDF or DOCX.
    Returns: JSON with combined LLM + NLP analysis results.
    """
    # Validate file presence
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Please select a resume file."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected. Please choose a file."}), 400

    # Validate extension
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({
            "error": f"Unsupported file type: '{ext}'.",
            "detail": f"Please upload a PDF (.pdf) or Word (.docx) file.",
        }), 400

    # Read file bytes
    try:
        file_bytes = file.read()
    except Exception as e:
        return jsonify({"error": f"Failed to read uploaded file: {str(e)}"}), 400

    # Validate file size (belt-and-suspenders with MAX_CONTENT_LENGTH)
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return jsonify({
            "error": f"File too large ({len(file_bytes) / 1024 / 1024:.1f} MB).",
            "detail": f"Maximum allowed size is {MAX_FILE_SIZE_MB} MB.",
        }), 400

    if len(file_bytes) == 0:
        return jsonify({"error": "The uploaded file is empty."}), 400

    # --- Processing Pipeline ---
    start_time = time.time()

    # Step 1: Extract text
    try:
        raw_text = extract_text_from_bytes(file_bytes, filename)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Document parsing failed: {str(e)}"}), 500

    # Step 2: Preprocess text
    cleaned_text = preprocess_resume_text(raw_text)

    if not cleaned_text.strip():
        return jsonify({
            "error": "No usable text could be extracted from the document.",
            "detail": "The file may be empty, contain only images, or be corrupted.",
        }), 422

    # Step 3: NLP analysis
    try:
        nlp_results = analyze_resume_nlp(cleaned_text)
    except Exception as e:
        nlp_results = {
            "skills": {"categorized": {}, "all_skills": [], "method": f"NLP failed: {e}"},
            "spacy_entities": [],
            "tfidf_keywords": {"keywords": [], "method": f"Failed: {e}"},
            "similarity": {
                "score": None, "percentage": "N/A",
                "matched_keywords": [], "missing_keywords": [],
                "method": f"Failed: {e}",
            },
        }

    # Step 4: LLM analysis
    try:
        llm_results = analyze_resume(cleaned_text)
    except Exception as e:
        llm_results = {"error": f"LLM analysis failed: {str(e)}"}

    processing_time = round(time.time() - start_time, 2)

    # Build response
    response = {
        "success": "error" not in llm_results,
        "filename": filename,
        "processing_time_seconds": processing_time,
        "text_stats": {
            "raw_characters": len(raw_text),
            "cleaned_characters": len(cleaned_text),
            "word_count": len(cleaned_text.split()),
        },
        "llm_analysis": llm_results,
        "nlp_analysis": {
            "skills_detected": nlp_results["skills"],
            "spacy_entities": nlp_results.get("spacy_entities", []),
            "tfidf_keywords": nlp_results["tfidf_keywords"],
            "similarity_score": nlp_results["similarity"],
        },
    }

    return jsonify(response)


@app.errorhandler(413)
def file_too_large(e):
    """Handle Flask's built-in file size limit error."""
    return jsonify({
        "error": f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB.",
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle unexpected server errors."""
    return jsonify({
        "error": "An unexpected error occurred. Please try again.",
    }), 500


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  AI Resume Analyzer — Web Interface")
    print(f"  http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"{'='*50}\n")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
