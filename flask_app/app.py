import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-fallback-key")

# Initialize Client pointing to Groq's Free API Engine
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

@app.route('/')
def index():
    # Added Telugu (te) to this list!
    languages = [
        {"code": "en", "name": "English"},
        {"code": "te", "name": "Telugu (తెలుగు)"},
        {"code": "hi", "name": "Hindi (हिन्दी)"},
        {"code": "es", "name": "Spanish (Español)"},
        {"code": "fr", "name": "French (Français)"},
        {"code": "de", "name": "German (Deutsch)"},
        {"code": "zh", "name": "Chinese (中文)"},
        {"code": "ja", "name": "Japanese (日本語)"},
        {"code": "ar", "name": "Arabic (العربية)"}
    ]
    return render_template('index.html', languages=languages)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    
    text = data.get('text', '').strip()
    source_lang = data.get('source_lang', 'Auto-Detect')
    target_lang = data.get('target_lang', 'English')
    
    if not text:
        return jsonify({'error': 'Text to translate cannot be empty.'}), 400

    try:
        system_instruction = (
            "You are an expert, multilingual AI translator. Your goal is to translate text accurately "
            "while fully preserving the original meaning, tone, context, and cultural nuances. "
            "Do not add any explanations, introductory remarks, or commentary. Output ONLY the translated text."
        )
        
        user_prompt = f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}"

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
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
        return jsonify({'error': f"An error occurred during translation: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)