from analyzer import analyze_resume
import json


def main():
    print("=== AI Resume Analyzer Agent (JSON Mode) ===\n")
    print("Paste your resume text below.")
    print("When finished, type END on a new line.\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    resume_text = "\n".join(lines)

    if not resume_text.strip():
        print("No resume text provided.")
        return

    print("\nAnalyzing resume...\n")

    result = analyze_resume(resume_text)

    print("\n=== Structured Analysis ===\n")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()