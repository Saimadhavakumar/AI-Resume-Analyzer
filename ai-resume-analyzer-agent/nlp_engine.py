# nlp_engine.py
# NLP and lightweight ML processing for resume analysis.
# Provides skill extraction, TF-IDF keyword analysis, and cosine similarity scoring.
# All scores include transparent explanations of how they were calculated.

import re
from collections import Counter

# ---------------------------------------------------------------------------
# Curated skill vocabulary — categorized for structured extraction
# ---------------------------------------------------------------------------

SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c\\+\\+", "c#", "c(?!\\w)",
        "ruby", "go", "golang", "rust", "swift", "kotlin", "scala", "php",
        "perl", "r(?!\\w)", "matlab", "lua", "dart", "haskell", "elixir",
        "objective-c", "assembly", "fortran", "cobol", "julia", "groovy",
        "visual basic", "vb\\.net", "bash", "shell", "powershell", "sql",
        "html", "css", "sass", "less",
    ],
    "Frameworks & Libraries": [
        "react", "angular", "vue", "vue\\.js", "svelte", "next\\.js", "nextjs",
        "nuxt", "gatsby", "django", "flask", "fastapi", "spring", "spring boot",
        "express", "express\\.js", "node\\.js", "nodejs", "rails", "ruby on rails",
        "laravel", "asp\\.net", "\\.net", "dotnet", "bootstrap", "tailwind",
        "jquery", "redux", "graphql", "rest", "restful",
        "streamlit", "gradio", "fasthtml",
    ],
    "Databases": [
        "mysql", "postgresql", "postgres", "mongodb", "redis", "sqlite",
        "oracle", "sql server", "mssql", "cassandra", "dynamodb",
        "elasticsearch", "neo4j", "firebase", "supabase", "cockroachdb",
        "mariadb", "couchdb", "influxdb",
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "gcp", "google cloud",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins",
        "ci/cd", "github actions", "gitlab ci", "circleci", "travis ci",
        "heroku", "vercel", "netlify", "nginx", "apache",
        "linux", "ubuntu", "centos", "cloudformation", "helm", "argocd",
        "prometheus", "grafana", "datadog", "new relic",
    ],
    "AI & ML": [
        "machine learning", "deep learning", "natural language processing",
        "nlp", "computer vision", "tensorflow", "pytorch", "keras",
        "scikit-learn", "sklearn", "pandas", "numpy", "scipy", "matplotlib",
        "seaborn", "hugging face", "huggingface", "transformers",
        "langchain", "openai", "gpt", "llama", "ollama", "bert",
        "lstm", "rnn", "cnn", "gan", "reinforcement learning",
        "xgboost", "lightgbm", "catboost", "opencv", "yolo",
        "rag", "fine-tuning", "fine tuning", "prompt engineering",
        "spacy", "nltk", "word2vec", "embeddings",
    ],
    "Tools & Platforms": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "slack", "notion", "figma", "postman", "swagger",
        "vscode", "visual studio", "intellij", "pycharm", "vim",
        "jupyter", "colab", "kaggle", "wandb", "mlflow",
        "tableau", "power bi", "excel", "google sheets",
        "webpack", "vite", "babel", "npm", "yarn", "pip", "conda",
        "selenium", "playwright", "cypress", "jest", "pytest",
        "unittest", "mocha", "chai",
    ],
}

# Flatten all skills into a single list for quick matching
ALL_SKILLS = {}
for category, skills in SKILL_CATEGORIES.items():
    for skill in skills:
        ALL_SKILLS[skill] = category


def extract_skills_regex(text: str) -> dict:
    """
    Extract skills from resume text using regex matching against a curated vocabulary.

    Returns:
        Dictionary with:
        - "categorized": dict mapping category names to lists of matched skills
        - "all_skills": flat list of all matched skills
        - "method": explanation of extraction method
    """
    text_lower = text.lower()
    found = {}

    for pattern, category in ALL_SKILLS.items():
        # Use word boundary matching for accurate detection
        regex = rf"\b{pattern}\b"
        try:
            if re.search(regex, text_lower, re.IGNORECASE):
                # Get the actual matched text to preserve casing hints
                match = re.search(regex, text_lower, re.IGNORECASE)
                skill_name = _normalize_skill_name(pattern, match.group())

                if category not in found:
                    found[category] = []
                if skill_name not in found[category]:
                    found[category].append(skill_name)
        except re.error:
            # Skip malformed patterns gracefully
            continue

    all_skills = []
    for skills in found.values():
        all_skills.extend(skills)

    return {
        "categorized": found,
        "all_skills": sorted(set(all_skills)),
        "method": "Regex matching against curated vocabulary of 150+ technical skills",
    }


def _normalize_skill_name(pattern: str, matched_text: str) -> str:
    """Convert regex patterns back to human-readable skill names."""
    # Map patterns to display names
    display_names = {
        "c\\+\\+": "C++",
        "c#": "C#",
        "c(?!\\w)": "C",
        "r(?!\\w)": "R",
        "vue\\.js": "Vue.js",
        "next\\.js": "Next.js",
        "express\\.js": "Express.js",
        "node\\.js": "Node.js",
        "\\.net": ".NET",
        "asp\\.net": "ASP.NET",
        "vb\\.net": "VB.NET",
    }

    if pattern in display_names:
        return display_names[pattern]

    # Title-case the matched text for readability
    # But preserve known acronyms
    acronyms = {
        "aws", "gcp", "sql", "css", "html", "php", "api", "rest",
        "ci/cd", "k8s", "nlp", "cnn", "rnn", "lstm", "gan", "npm",
        "rag", "gpt", "bert", "yolo", "mlflow",
    }
    if matched_text.lower() in acronyms:
        return matched_text.upper()

    return matched_text.title()


def extract_skills_spacy(text: str) -> list:
    """
    Extract additional entities from resume text using spaCy NER.

    Identifies organizations, products, and other named entities that
    may represent technologies, companies, or certifications not in
    the curated vocabulary.

    Returns:
        List of extracted entity strings, or empty list if spaCy unavailable.
    """
    try:
        import spacy
    except ImportError:
        return []

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Model not installed
        return []

    doc = nlp(text)

    # Extract relevant entity types
    relevant_labels = {"ORG", "PRODUCT", "WORK_OF_ART", "EVENT"}
    entities = []

    for ent in doc.ents:
        if ent.label_ in relevant_labels and len(ent.text) > 1:
            clean = ent.text.strip()
            if clean and clean not in entities:
                entities.append(clean)

    return entities


def compute_tfidf_keywords(text: str, top_n: int = 20) -> dict:
    """
    Compute TF-IDF scores for resume text to identify the most
    distinctive keywords in the document.

    Uses scikit-learn's TfidfVectorizer with a reference corpus of
    generic text to calculate meaningful IDF weights.

    Args:
        text: The resume text to analyze.
        top_n: Number of top keywords to return.

    Returns:
        Dictionary with:
        - "keywords": list of (keyword, score) tuples sorted by TF-IDF score
        - "method": explanation of the calculation
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        return {
            "keywords": [],
            "method": "TF-IDF unavailable (scikit-learn not installed)",
        }

    # Reference corpus — generic text for IDF contrast
    # The resume is compared against these to find its distinctive terms
    reference_docs = [
        "The candidate has experience working in a team environment with "
        "good communication skills and problem solving abilities.",
        "Responsible for managing projects and delivering results on time. "
        "Strong leadership and organizational skills demonstrated.",
        "Proficient in various technologies and tools with hands-on experience "
        "in software development and engineering practices.",
        "Education background includes degree in computer science or related "
        "field with relevant coursework and academic projects.",
    ]

    corpus = reference_docs + [text]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=500,
        ngram_range=(1, 2),  # Unigrams and bigrams
        min_df=1,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z+#.]{1,}\b",  # Allow C++, C#, .NET
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()

        # Get scores for the resume (last document)
        resume_scores = tfidf_matrix[-1].toarray().flatten()

        # Pair features with scores and sort
        scored_keywords = [
            (feature_names[i], round(float(resume_scores[i]), 4))
            for i in range(len(feature_names))
            if resume_scores[i] > 0
        ]
        scored_keywords.sort(key=lambda x: x[1], reverse=True)

        return {
            "keywords": scored_keywords[:top_n],
            "method": (
                "TF-IDF (Term Frequency-Inverse Document Frequency) calculated "
                "against a reference corpus of generic resume phrases. Higher scores "
                "indicate terms that are more distinctive to this specific resume."
            ),
        }
    except Exception:
        return {
            "keywords": [],
            "method": "TF-IDF computation failed",
        }


def compute_similarity_score(resume_text: str, job_keywords: list = None) -> dict:
    """
    Compute cosine similarity between the resume and a target keyword set.

    If no job_keywords are provided, uses a curated set of high-value
    software engineering keywords as the comparison target.

    Args:
        resume_text: The cleaned resume text.
        job_keywords: Optional list of target keywords/phrases.

    Returns:
        Dictionary with:
        - "score": float between 0 and 1
        - "percentage": human-readable percentage string
        - "matched_keywords": list of target keywords found in the resume
        - "missing_keywords": list of target keywords NOT found
        - "method": explanation of the calculation
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        return {
            "score": None,
            "percentage": "N/A",
            "matched_keywords": [],
            "missing_keywords": [],
            "method": "Cosine similarity unavailable (scikit-learn not installed)",
        }

    if job_keywords is None:
        # Default target: a well-rounded software engineering profile
        job_keywords = [
            "python", "javascript", "java", "sql", "api", "rest",
            "git", "docker", "cloud", "aws", "database",
            "machine learning", "data structures", "algorithms",
            "testing", "agile", "ci/cd", "linux",
            "problem solving", "teamwork", "communication",
            "scalable", "performance", "security",
        ]

    target_text = " ".join(job_keywords)
    resume_lower = resume_text.lower()

    # Find which keywords are present/missing
    matched = [kw for kw in job_keywords if kw.lower() in resume_lower]
    missing = [kw for kw in job_keywords if kw.lower() not in resume_lower]

    # Compute cosine similarity between resume and target
    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, target_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = round(float(similarity[0][0]), 4)
    except Exception:
        score = 0.0

    return {
        "score": score,
        "percentage": f"{score * 100:.1f}%",
        "matched_keywords": matched,
        "missing_keywords": missing,
        "method": (
            "Cosine similarity between TF-IDF vectors of the resume text "
            "and a target keyword set representing a well-rounded software "
            f"engineering profile ({len(job_keywords)} target keywords). "
            f"Matched {len(matched)}/{len(job_keywords)} keywords."
        ),
    }


def analyze_resume_nlp(text: str) -> dict:
    """
    Run the full NLP analysis pipeline on resume text.

    This function is the main entry point for the NLP engine.
    It combines:
    1. Regex-based skill extraction (curated vocabulary)
    2. spaCy NER entity extraction (if available)
    3. TF-IDF keyword analysis
    4. Cosine similarity scoring

    Args:
        text: Cleaned resume text.

    Returns:
        Dictionary containing all NLP analysis results.
    """
    if not text or not text.strip():
        return {
            "skills": {"categorized": {}, "all_skills": [], "method": "N/A"},
            "spacy_entities": [],
            "tfidf_keywords": {"keywords": [], "method": "N/A"},
            "similarity": {
                "score": None,
                "percentage": "N/A",
                "matched_keywords": [],
                "missing_keywords": [],
                "method": "N/A",
            },
        }

    skills = extract_skills_regex(text)
    spacy_entities = extract_skills_spacy(text)
    tfidf = compute_tfidf_keywords(text)
    similarity = compute_similarity_score(text)

    return {
        "skills": skills,
        "spacy_entities": spacy_entities,
        "tfidf_keywords": tfidf,
        "similarity": similarity,
    }
