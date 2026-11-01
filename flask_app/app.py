
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-fallback-key")

# Initialize Groq API client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# Supported languages
SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "te", "name": "Telugu (తెలుగు)"},
    {"code": "hi", "name": "Hindi (हिन्दी)"},
    {"code": "ta", "name": "Tamil (தமிழ்)"},
    {"code": "kn", "name": "Kannada (ಕನ್ನಡ)"},
    {"code": "mr", "name": "Marathi (मराठी)"},
    {"code": "ml", "name": "Malayalam (മലയാളം)"},
    {"code": "bn", "name": "Bengali (বাংলা)"},
    {"code": "gu", "name": "Gujarati (ગુજરાતી)"},
    {"code": "pa", "name": "Punjabi (ਪੰਜਾਬੀ)"},
    {"code": "or", "name": "Odia (ଓଡ଼ିଆ)"},
    {"code": "ur", "name": "Urdu (اردو)"},
    {"code": "as", "name": "Assamese (অসমীয়া)"},
    {"code": "ne", "name": "Nepali (नेपाली)"},
    {"code": "sa", "name": "Sanskrit (संस्कृतम्)"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "zh", "name": "Chinese"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ar", "name": "Arabic"}
]


# Home page
@app.route('/')
def index():
    return render_template(
        'index.html',
        languages=SUPPORTED_LANGUAGES
    )


# Translation API
@app.route('/translate', methods=['POST'])
def translate_text():

    data = request.get_json(silent=True) or {}

    text = data.get('text', '').strip()
    source_lang = data.get('source_lang', 'Auto-Detect')
    target_lang = data.get('target_lang', 'English')

    # Validate input
    if not text:
        return jsonify({
            'error': 'Text to translate cannot be empty.'
        }), 400

    if not os.getenv("GROQ_API_KEY"):
        return jsonify({
            'error': 'GROQ_API_KEY is missing. Please configure your .env file.'
        }), 500

    try:
        system_instruction = (
            "You are an expert multilingual AI translator. "
            "Translate text accurately while preserving its original meaning, "
            "tone, context, and cultural nuances. "
            "Use natural grammar and the correct native writing script. "
            "For Indian languages, write using their proper native scripts, "
            "not English-letter transliteration. "
            "Do not add explanations, introductions, or commentary. "
            "Return only the translated text."
        )

        user_prompt = f"""
Translate the following text.

Source language: {source_lang}
Target language: {target_lang}

Instructions:
- If the source language is Auto-Detect, identify it automatically.
- Preserve the original meaning and context.
- Use natural grammar.
- Use the correct native script of the target language.
- Do not translate names unnecessarily.
- Return only the translated text.

Text:
{text}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.3,
        )

        translated_text = response.choices[0].message.content.strip()

        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang
        })

    except Exception as e:
        return jsonify({
            'error': f"An error occurred during translation: {str(e)}"
        }), 500


# Run Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5000)
