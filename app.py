from flask import Flask, render_template, request
import PyPDF2
import docx
import json

app = Flask(__name__)

# Load JSON
with open("data.json") as f:
    data = json.load(f)

learning_links = data["learning_links"]
job_links = data["job_links"]

def read_pdf(file):
    text = ""
    pdf = PyPDF2.PdfReader(file)
    for page in pdf.pages:
        t = page.extract_text()
        if t:
            text += t
    return text

def read_docx(file):
    doc = docx.Document(file)
    return " ".join([p.text for p in doc.paragraphs])

@app.route("/", methods=["GET", "POST"])
def index():
    found = []
    missing = []
    score = 0
    ats = 0
    learning = []
    jobs = []
    summary = ""
    fake_warning = ""
    if request.method == "POST":
        file = request.files["resume"]
        job_desc = request.form.get("job_desc", "").lower()

        # Read file
        if file.filename.endswith(".pdf"):
            text = read_pdf(file)
        elif file.filename.endswith(".docx"):
            text = read_docx(file)
        else:
            text = ""

        text = text.lower()

        skills = ["python", "html", "css", "javascript", "react", "node"]

        for s in skills:
            if s in text:
                found.append(s)
            else:
                missing.append(s)

        # Score
        if skills:
            score = int((len(found) / len(skills)) * 100)

        # 🔥 Fake Resume Detector
        if len(found) >= 4 and "project" not in text and "experience" not in text:
            fake_warning = "⚠️ This resume may be unrealistic. Add projects or experience to support your skills."

        # ATS
        if job_desc:
            res_words = set(text.split())
            jd_words = set(job_desc.split())
            if jd_words:
                ats = int((len(res_words & jd_words) / len(jd_words)) * 100)

        # Learning links
        for m in missing:
            if m in learning_links:
                learning.append((m, learning_links[m]))

        # Jobs
        jobs = job_links.get("web_dev", [])

        # Summary
        if found:
            summary = "You have skills in " + ", ".join(found)

    return render_template("index.html",
                           found=found,
                           missing=missing,
                           score=score,
                           ats=ats,
                           learning=learning,
                           jobs=jobs,
                           summary=summary,
                           fake_warning=fake_warning)

if __name__ == "__main__":
    app.run(debug=True)