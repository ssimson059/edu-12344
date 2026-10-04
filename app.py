import os, re, json
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()  # optional: reads GEMINI_API_KEY from a local .env file
BASE = Path(__file__).parent

# ---- Domain configuration (edit this to customise the bot) ----
CFG = json.loads(r'''{
  "name": "Education Helper",
  "bot": "EduBot",
  "color": "#4f46e5",
  "greeting": "Hello! I'm EduBot. Ask me about courses, admissions, exam preparation or study tips.",
  "chips": [
    "Admission process",
    "Study tips",
    "Exam schedule",
    "Scholarships"
  ],
  "fallback": "I can help with admissions, courses, exams, scholarships and study tips. Try asking one of those.",
  "system_prompt": "You are EduBot, a helpful student support assistant for a college or school. Help with admissions, courses, exams, study tips and campus info. Be encouraging and clear. Answer only questions related to this domain; politely redirect anything else. Keep replies short (under 120 words), clear and friendly.",
  "faq": [
    {
      "keywords": [
        "admission",
        "apply",
        "enroll"
      ],
      "answer": "Admission steps: 1) fill the online application, 2) upload marksheets and ID, 3) pay the application fee, 4) attend counselling or an interview if required, 5) pay the course fee to confirm your seat."
    },
    {
      "keywords": [
        "course",
        "program",
        "degree",
        "department"
      ],
      "answer": "We offer undergraduate and postgraduate programs in Engineering, Science, Commerce, Arts and Management. Ask about a specific department for details."
    },
    {
      "keywords": [
        "exam",
        "timetable",
        "schedule"
      ],
      "answer": "Exam timetables are published on the student portal at least 2 weeks before exams. Keep your hall ticket and ID card ready."
    },
    {
      "keywords": [
        "study",
        "tips",
        "focus",
        "concentrate"
      ],
      "answer": "Study in 25-minute focused blocks with 5-minute breaks, revise using active recall, sleep at least 7 hours, and solve past papers before exams."
    },
    {
      "keywords": [
        "scholarship",
        "fee waiver",
        "financial aid"
      ],
      "answer": "Scholarships are available for merit, sports and economically weaker students. Submit income and marks documents to the scholarship cell before the deadline."
    },
    {
      "keywords": [
        "library",
        "book"
      ],
      "answer": "The library is open 8:30 AM to 8:00 PM on weekdays. Students can borrow up to 4 books for 14 days with their ID card."
    },
    {
      "keywords": [
        "placement",
        "job",
        "career"
      ],
      "answer": "The placement cell runs aptitude training, mock interviews and campus drives every semester. Keep your resume updated on the portal."
    },
    {
      "keywords": [
        "hostel",
        "accommodation"
      ],
      "answer": "Hostel rooms are allotted on a first-come basis after admission confirmation. Apply through the hostel office with your admission receipt."
    }
  ]
}''')

app = Flask(__name__)
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()


def local_answer(message: str) -> str:
    """Offline fallback: pick the FAQ entry with the most keyword hits."""
    text = message.lower()
    best, best_score = None, 0
    for item in CFG["faq"]:
        score = sum(1 for k in item["keywords"] if k in text)
        if score > best_score:
            best, best_score = item, score
    return best["answer"] if best else CFG["fallback"]


def gemini_answer(message: str, history: list) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    contents = []
    for turn in history[-10:]:
        role = "user" if turn.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": str(turn.get("text", ""))}]})
    contents.append({"role": "user", "parts": [{"text": message}]})
    body = {
        "systemInstruction": {"parts": [{"text": CFG["system_prompt"]}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 600},
    }
    r = requests.post(url, headers={"x-goog-api-key": API_KEY}, json=body, timeout=30)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


@app.get("/")
def index():
    return send_from_directory(BASE, "index.html")


@app.get("/style.css")
def style():
    return send_from_directory(BASE, "style.css")


@app.get("/script.js")
def script():
    return send_from_directory(BASE, "script.js")


@app.get("/api/config")
def config():
    return jsonify({k: CFG[k] for k in ("name", "bot", "color", "greeting", "chips")})


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []
    if not message:
        return jsonify({"error": "Message is empty."}), 400
    if API_KEY:
        try:
            return jsonify({"reply": gemini_answer(message, history), "source": "gemini"})
        except Exception as exc:  # fall back to local answers
            print("Gemini error:", exc)
    return jsonify({"reply": local_answer(message), "source": "local"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
