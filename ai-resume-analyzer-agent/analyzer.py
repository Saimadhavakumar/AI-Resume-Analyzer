# analyzer.py

import ollama
import json
import re
from config import OLLAMA_MODEL, TEMPERATURE, MAX_TOKENS


def analyze_resume(resume_text: str) -> dict:

    prompt = f"""
You are a senior technical recruiter.

Analyze the following resume deeply and critically.

IMPORTANT:
- Do NOT simply copy text from the resume.
- Infer suitable future job roles based on skills and experience.
- Identify real gaps for software engineering / AI industry.
- Provide meaningful improvement advice.

Return ONLY valid JSON.
Do NOT include explanations outside JSON.

Structure:

{{
  "skills": [],
  "roles": [],
  "strengths": [],
  "gaps": [],
  "improvement_plan": [],
  "ats_tips": []
}}

Rules:
- Each field must be a list of concise but meaningful strings.
- Roles must be SUGGESTED FUTURE ROLES, not existing internship titles.
- Gaps must reflect real industry expectations.
- Improvement plan must be actionable and technical.

Resume:
{resume_text}
"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS
            }
        )

        raw_output = response["message"]["content"]

        # Extract JSON safely
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

        if not json_match:
            return {
                "error": "No JSON found in model output",
                "raw_output": raw_output
            }

        json_str = json_match.group()

        try:
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON format",
                "raw_output": raw_output
            }

    except Exception as e:
        return {"error": str(e)}