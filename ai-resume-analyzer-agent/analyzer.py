# analyzer.py
# Core Ollama/Llama 3 resume analysis engine with candidate-specific dynamic NLP fallback.

import ollama
import json
import re
from config import OLLAMA_MODEL, TEMPERATURE, MAX_TOKENS
from nlp_engine import analyze_resume_nlp

# The JSON schema the LLM is instructed to return
ANALYSIS_SCHEMA = {
    "summary": "string — concise profile description tailored to candidate",
    "strengths": ["list of concrete strengths supported by the resume"],
    "weaknesses": ["list of concrete weaknesses or missing information"],
    "skills": {
        "programming_languages": [],
        "frameworks_libraries": [],
        "databases": [],
        "cloud_devops": [],
        "ai_ml": [],
        "tools": [],
        "other": [],
    },
    "experience_analysis": {
        "relevance": "string",
        "clarity": "string",
        "impact": "string",
        "technical_depth": "string",
        "measurable_achievements": "string",
    },
    "projects_analysis": {
        "technical_relevance": "string",
        "technologies_used": [],
        "clarity": "string",
        "measurable_impact": "string",
        "engineering_ability": "string",
    },
    "education": "string — relevant education summary",
    "certifications": ["list of identified certifications"],
    "improvement_suggestions": ["list of actionable recommendations"],
    "ats_observations": ["list of ATS-related observations"],
    "suggested_roles": ["list of suitable future job roles"],
}


def _build_analysis_prompt(resume_text: str) -> str:
    """Build the analysis prompt with strict candidate-specific requirements."""
    schema_str = json.dumps(ANALYSIS_SCHEMA, indent=2)

    prompt = f"""You are a senior technical recruiter analyzing this specific candidate's resume.

IMPORTANT: Your response must be 100% custom and uniquely tailored to THIS candidate's exact experience, projects, and skills. Do NOT output generic boilerplate.

Resume:
{resume_text}

Rules:
- In "summary", reference the candidate's exact background, title, and key technical stack.
- In "strengths", list 3-5 specific achievements, skill combinations, or strengths found in their resume.
- In "weaknesses", list 3-5 real gaps (missing technologies, lack of metrics, formatting gaps).
- In "skills", group detected skills into the specified subcategories.
- In "experience_analysis" and "projects_analysis", evaluate the actual projects and roles described in their text.
- In "suggested_roles", suggest 3-5 roles that logically match their technical stack.
- In "improvement_suggestions", provide actionable, highly specific advice tailored to their missing elements.
- In "ats_observations", highlight specific keyword or layout observations for this document.

Return ONLY valid JSON matching this schema:
{schema_str}"""

    return prompt


def _extract_json_from_response(raw_output: str) -> str:
    """Extract JSON from LLM response using multiple strategies."""
    stripped = raw_output.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            json.loads(stripped)
            return stripped
        except json.JSONDecodeError:
            pass

    code_block_match = re.search(
        r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw_output, re.DOTALL
    )
    if code_block_match:
        candidate = code_block_match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass

    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if json_match:
        candidate = json_match.group()
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            cleaned = _cleanup_json(candidate)
            if cleaned:
                return cleaned

    return None


def _cleanup_json(json_str: str) -> str:
    """Attempt to fix common JSON syntax errors."""
    cleaned = re.sub(r",\s*([}\]])", r"\1", json_str)
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        pass

    try:
        if '"' not in cleaned:
            cleaned = cleaned.replace("'", '"')
            json.loads(cleaned)
            return cleaned
    except json.JSONDecodeError:
        pass

    return None


def _parse_resume_sections(text: str) -> dict:
    """
    Parse resume text into structural sections:
    Header/Name, Summary, Experience, Projects, Education, Certifications, Skills.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    sections = {
        "header": "",
        "summary": "",
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
    }

    if not lines:
        return sections

    # First non-empty line usually contains candidate name / title
    sections["header"] = lines[0]
    if len(lines) > 1 and not any(k in lines[1].lower() for k in ["experience", "education", "skill", "project"]):
        sections["header"] += f" - {lines[1]}"

    current_section = "other"
    for line in lines:
        l_lower = line.lower()
        if any(h in l_lower for h in ["experience", "employment", "work history", "work experience"]):
            current_section = "experience"
            continue
        elif any(h in l_lower for h in ["projects", "personal projects", "academic projects", "key projects"]):
            current_section = "projects"
            continue
        elif any(h in l_lower for h in ["education", "academic", "qualification"]):
            current_section = "education"
            continue
        elif any(h in l_lower for h in ["certification", "certificates", "licenses"]):
            current_section = "certifications"
            continue
        elif any(h in l_lower for h in ["summary", "profile", "about me", "objective"]):
            current_section = "summary"
            continue

        if current_section in sections and isinstance(sections[current_section], list):
            sections[current_section].append(line)
        elif current_section == "summary":
            sections["summary"] += " " + line

    return sections


def generate_fallback_analysis(resume_text: str, nlp_results: dict = None) -> dict:
    """
    Generate dynamic, highly candidate-specific resume analysis using NLP extraction.
    Ensures every candidate receives unique, non-generic feedback.
    """
    if nlp_results is None:
        nlp_results = analyze_resume_nlp(resume_text)

    skills_dict = nlp_results.get("skills", {}).get("categorized", {})
    all_skills = nlp_results.get("skills", {}).get("all_skills", [])
    sim = nlp_results.get("similarity", {})

    parsed = _parse_resume_sections(resume_text)

    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
    text_lower = resume_text.lower()

    # --- 1. Dynamic Role Suggestions ---
    suggested_roles = []
    prog = [s.lower() for s in skills_dict.get("Programming Languages", [])]
    fw = [s.lower() for s in skills_dict.get("Frameworks & Libraries", [])]
    db = [s.lower() for s in skills_dict.get("Databases", [])]
    cloud = [s.lower() for s in skills_dict.get("Cloud & DevOps", [])]
    ai = [s.lower() for s in skills_dict.get("AI & ML", [])]

    if ai or any(k in text_lower for k in ["machine learning", "nlp", "llm", "deep learning", "pytorch", "tensorflow"]):
        suggested_roles.extend(["AI / ML Engineer", "Data Scientist", "NLP Specialist"])
    if ("react" in fw or "vue" in fw or "angular" in fw or "next.js" in fw) and ("python" in prog or "node.js" in fw or "java" in prog or "express.js" in fw):
        suggested_roles.append("Full-Stack Software Engineer")
    if "python" in prog or "django" in fw or "flask" in fw or "fastapi" in fw:
        suggested_roles.append("Backend Developer (Python)")
    if "java" in prog or "spring" in fw:
        suggested_roles.append("Java Enterprise Developer")
    if "javascript" in prog or "typescript" in prog or "react" in fw:
        suggested_roles.append("Frontend Engineer")
    if cloud or "docker" in text_lower or "kubernetes" in text_lower:
        suggested_roles.append("Cloud / DevOps Engineer")

    if not suggested_roles:
        suggested_roles = ["Software Development Engineer (SDE)", "Junior Developer", "Technical Analyst"]

    # --- 2. Candidate-Specific Profile Summary ---
    candidate_identifier = parsed["header"] if parsed["header"] else "The candidate"
    primary_category = ""
    if ai:
        primary_category = "AI/ML and Data Science"
    elif fw and prog:
        primary_category = "Full-Stack Software Development"
    elif prog:
        primary_category = f"Software Engineering ({', '.join(skills_dict.get('Programming Languages', [])[:3])})"
    else:
        primary_category = "Technical Engineering"

    top_tech = ", ".join(all_skills[:6]) if all_skills else "core programming tools"
    word_cnt = len(resume_text.split())

    summary_str = (
        f"{candidate_identifier} presents a profile focused on {primary_category}. "
        f"Demonstrates hands-on skills in {top_tech}. "
        f"The resume ({word_cnt} words) reflects strong technical alignment with candidate targets such as {', '.join(suggested_roles[:2])}."
    )

    # --- 3. Dynamic Strengths ---
    strengths = []
    if skills_dict.get("Programming Languages"):
        strengths.append(f"Multi-language proficiency in {', '.join(skills_dict['Programming Languages'])}.")
    if skills_dict.get("Frameworks & Libraries"):
        strengths.append(f"Modern framework stack including {', '.join(skills_dict['Frameworks & Libraries'])}.")
    if skills_dict.get("Cloud & DevOps") or skills_dict.get("Databases"):
        tools = (skills_dict.get("Cloud & DevOps", []) + skills_dict.get("Databases", []))[:4]
        strengths.append(f"Backend & infrastructure experience with {', '.join(tools)}.")

    # Check for quantitative metrics in text
    metrics_matches = re.findall(r"\b(\d+%\b|\$\d+|\b\d+\s*users?\b|\b\d+x\b|\b\d+\s*ms\b)", resume_text, re.IGNORECASE)
    if metrics_matches:
        strengths.append(f"Includes measurable achievement metrics (e.g. {', '.join(set(metrics_matches[:3]))}).")
    else:
        strengths.append(f"Solid foundational technical coverage with {len(all_skills)} detected industry keywords.")

    if parsed["projects"]:
        strengths.append(f"Includes documented project work ({len(parsed['projects'])} project bullet points).")

    # --- 4. Dynamic Weaknesses / Gaps ---
    weaknesses = []
    if not metrics_matches:
        weaknesses.append("Lacks quantitative metrics (e.g. '% speedup', 'users handled', '$ revenue') to prove project impact.")
    if not skills_dict.get("Cloud & DevOps"):
        weaknesses.append("Missing cloud deployment & containerization skills (AWS, Docker, Kubernetes, CI/CD).")
    if not skills_dict.get("Databases"):
        weaknesses.append("No explicit database management tools (PostgreSQL, MongoDB, Redis, MySQL) detected.")
    if not any("git" in s.lower() for s in all_skills):
        weaknesses.append("Version control (Git/GitHub) is not explicitly highlighted in technical skills.")
    if len(all_skills) < 8:
        weaknesses.append(f"Technical keyword count is lower than average ({len(all_skills)} skills). Expand technical inventory.")

    # --- 5. Candidate-Specific Experience Analysis ---
    action_verbs_found = [v for v in ["developed", "built", "designed", "implemented", "optimized", "engineered", "created", "led", "architected"] if v in text_lower]

    exp_analysis = {
        "relevance": f"Experience matches key requirements for {suggested_roles[0]} roles.",
        "clarity": f"Resume contains {len(lines)} structured content lines.",
        "impact": (
            f"Uses strong action verbs ({', '.join(action_verbs_found[:4])})."
            if action_verbs_found
            else "Experience descriptions rely on passive phrasing. Replace with action verbs like 'Engineered', 'Architected'."
        ),
        "technical_depth": f"Demonstrates technical application in {', '.join(all_skills[:4]) if all_skills else 'software development'}.",
        "measurable_achievements": (
            f"Quantitative metrics found: {', '.join(set(metrics_matches[:3]))}."
            if metrics_matches
            else "No numeric metrics identified in experience text. Add performance percentages or scale figures."
        ),
    }

    # --- 6. Candidate-Specific Projects Analysis ---
    proj_lines = parsed["projects"] if parsed["projects"] else lines
    proj_tech = [s for s in all_skills if any(s.lower() in l.lower() for l in proj_lines)]

    proj_analysis = {
        "technical_relevance": f"Project portfolio aligns with {primary_category}.",
        "technologies_used": proj_tech if proj_tech else (all_skills[:5] if all_skills else ["Python", "JavaScript"]),
        "clarity": "Project section is present with readable descriptions." if parsed["projects"] else "Consider creating a dedicated 'Projects' section header.",
        "measurable_impact": "Add repository links (GitHub/GitLab) and live demo links to validate project impact." if not any("github" in l.lower() for l in lines) else "GitHub/repository links present.",
        "engineering_ability": f"Demonstrates practical implementation using {', '.join(all_skills[:3]) if all_skills else 'core programming'}.",
    }

    # --- 7. Education Extraction ---
    edu_found = parsed["education"] if parsed["education"] else [l for l in lines if any(k in l.lower() for k in ["bachelor", "master", "b.tech", "b.e.", "b.s.", "m.s.", "degree", "university", "college", "institute"])]
    education_str = " | ".join(edu_found[:3]) if edu_found else "Academic credentials present in document."

    # --- 8. Certifications Extraction ---
    cert_found = parsed["certifications"] if parsed["certifications"] else [l for l in lines if any(k in l.lower() for k in ["certified", "certification", "certificate", "coursera", "udemy", "nptel", "aws certified"])]

    # --- 9. Dynamic Improvement Suggestions ---
    improvements = []
    if not metrics_matches:
        improvements.append("Add quantifiable outcome metrics to bullet points (e.g. 'Reduced loading time by 35%').")
    if not skills_dict.get("Cloud & DevOps"):
        improvements.append("Add cloud deployment skills (AWS, Docker, CI/CD) to align with modern engineering jobs.")
    if not any("github.com" in l.lower() for l in lines):
        improvements.append("Include full GitHub profile or project repository links for recruiter code verification.")
    target_role_str = suggested_roles[0] if len(suggested_roles) == 1 else f"{suggested_roles[0]} or {suggested_roles[1]}"
    improvements.append(f"Tailor target title specifically for {target_role_str} roles.")

    # --- 10. Dynamic ATS Observations ---
    ats_obs = [
        f"Document length is {word_cnt} words ({len(lines)} lines), fitting standard single or multi-page formats.",
        f"Detected {len(all_skills)} technical keywords across {len(skills_dict)} categories.",
        "Ensure standard header terms like 'Work Experience', 'Technical Skills', and 'Education' are capitalized.",
    ]

    # Format skills into standard subcategories
    formatted_skills = {
        "programming_languages": skills_dict.get("Programming Languages", []),
        "frameworks_libraries": skills_dict.get("Frameworks & Libraries", []),
        "databases": skills_dict.get("Databases", []),
        "cloud_devops": skills_dict.get("Cloud & DevOps", []),
        "ai_ml": skills_dict.get("AI & ML", []),
        "tools": skills_dict.get("Tools & Platforms", []),
        "other": [],
    }

    return {
        "summary": summary_str,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "skills": formatted_skills,
        "experience_analysis": exp_analysis,
        "projects_analysis": proj_analysis,
        "education": education_str,
        "certifications": cert_found if cert_found else ["No formal certifications explicitly detected."],
        "improvement_suggestions": improvements,
        "ats_observations": ats_obs,
        "suggested_roles": suggested_roles,
        "is_fallback": True,
    }


def analyze_resume(resume_text: str) -> dict:
    """
    Analyze resume text using Ollama/Llama 3 with dynamic NLP fallback.

    Uses candidate-specific structural parsing and NLP evaluation to ensure
    every resume receives unique, non-generic feedback.
    """
    nlp_results = analyze_resume_nlp(resume_text)
    prompt = _build_analysis_prompt(resume_text)

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS,
            },
        )

        raw_output = response["message"]["content"]
        json_str = _extract_json_from_response(raw_output)

        if json_str:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict) and "summary" in parsed:
                parsed["is_fallback"] = False
                return parsed

    except Exception:
        pass

    return generate_fallback_analysis(resume_text, nlp_results)