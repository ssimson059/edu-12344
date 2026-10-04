# Education Helper (EduBot)

A simple domain chatbot built with a Python (Flask) backend and an HTML/CSS/JS frontend.
It uses the Gemini API when a key is set. Without a key it answers from the built-in
keyword FAQ (offline mode), so it works out of the box.

## Project structure
```
index.html        chat page
style.css         styles
script.js         frontend logic
app.py            Flask server, Gemini call, offline FAQ
requirements.txt  Python dependencies
README.md         this file
.gitignore        keeps .env and cache files out of git
```

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Enable Gemini (optional)
1. Get a free key at https://aistudio.google.com/apikey
2. Create a file named `.env` next to `app.py`:
```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
```
3. Restart `python app.py`. The badge in the header changes from "Offline mode" to "Gemini".

`.env` is listed in `.gitignore`, so your key will not be committed.

## Customise
Edit the `CFG` block at the top of `app.py`: bot name, color, greeting, quick-reply chips,
FAQ keywords/answers and the Gemini system prompt.
