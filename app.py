from flask import Flask, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename
import os
import pyttsx3
import json
import re
from utils.ocr_utils import extract_text_from_scanned_pdf
from utils.clean_utils import clean_text
from utils.auto_faq_builder import generate_faq_from_text
from rapidfuzz import fuzz

app = Flask(__name__)

# Configure upload and output folders
app.config['UPLOAD_FOLDER'] = 'data'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('output', exist_ok=True)

MAX_TEXT_LENGTH = 4500  # Limit text length for TTS

@app.route('/')
def index():
    # Render home page with no audio and no chatbot active initially
    return render_template('index.html', audio_file=None, chatbot_mode=False, error=None)

@app.route('/process', methods=['POST'])
def process():
    uploaded_file = request.files.get('file')
    language = request.form.get('language')
    mode = request.form.get('mode')

    if not uploaded_file:
        return render_template('index.html', audio_file=None, chatbot_mode=False, error="No file uploaded")

    filename = secure_filename(uploaded_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(filepath)

    try:
        # Extract text from scanned PDF using OCR
        raw_text = extract_text_from_scanned_pdf(filepath)

        # Remove page markers after OCR, before cleaning
        raw_text = re.sub(r'-{3} Page \d+ -{3}', '', raw_text)
        raw_text = raw_text.strip()

        if not raw_text:
            raise ValueError("OCR returned empty text.")
    except Exception as e:
        return render_template('index.html', audio_file=None, chatbot_mode=False, error=f"OCR failed: {str(e)}")

    # Clean extracted text
    cleaned_text = clean_text(raw_text)

    # Generate FAQ JSON file from cleaned text
    generate_faq_from_text(cleaned_text)

    if mode == 'audio':
        try:
            # Initialize pyttsx3 TTS engine
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)  # Default voice

            audio_filename = 'output.wav'
            audio_path = os.path.join('static', audio_filename)

            # Remove previous audio file if exists
            if os.path.exists(audio_path):
                os.remove(audio_path)

            # Save TTS audio to file (limit length)
            engine.save_to_file(cleaned_text[:MAX_TEXT_LENGTH], audio_path)
            engine.runAndWait()

            if not os.path.exists(audio_path):
                raise Exception("Audio file was not created.")

            return render_template('index.html', audio_file=url_for('static', filename=audio_filename), chatbot_mode=False, error=None)
        except Exception as e:
            return render_template('index.html', audio_file=None, chatbot_mode=False, error=f"Audio error: {str(e)}")

    elif mode == 'chatbot':
        # Render page with chatbot enabled
        return render_template('index.html', audio_file=None, chatbot_mode=True, error=None)

    # Default fallback if mode not recognized
    return render_template('index.html', audio_file=None, chatbot_mode=False, error="Invalid mode selected")

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question', '').lower()

    def format_as_bullets(text):
        # Format answer text as bullets if colon-separated list present
        if ':' in text:
            content = text.split(':', 1)[1]
            bullets = [f"• {line.strip().capitalize()}" for line in content.split(',') if line.strip()]
            return '\n'.join(bullets)
        return text

    try:
        # Load FAQ knowledge base
        with open("output/faq_knowledge.json", "r", encoding="utf-8") as f:
            faqs = json.load(f)

        best_match = None
        highest_score = 0

        # Find best fuzzy match for question
        for q, a in faqs.items():
            score = fuzz.partial_ratio(question, q.lower())
            if score > highest_score:
                highest_score = score
                best_match = a

        if best_match and highest_score >= 60:
            return jsonify({"answer": format_as_bullets(best_match)})
        else:
            return jsonify({"answer": "I'm sorry, I couldn't find an answer for that."})

    except Exception as e:
        return jsonify({"answer": f"Error loading knowledge base: {str(e)}"})

if __name__ == '__main__':
    print(" Flask App running at http://127.0.0.1:5000")
    app.run(debug=True)
