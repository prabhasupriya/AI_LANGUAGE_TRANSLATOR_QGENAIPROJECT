import os
import gradio as gr
from groq import Groq
from dotenv import load_dotenv

# Load secret environment variables (.env file from project root)
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Initialize the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def voice_translator_engine(audio_path, target_language):
    if audio_path is None:
        return "⚠️ Error: Please record your voice before clicking Translate!", ""

    try:
        # --- PHASE 1: Speech-to-Text (Auto-Detect Language) ---
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), file.read()),
                model="whisper-large-v3", 
                # Removing language="en" allows Whisper to automatically detect 
                # whatever language the user speaks!
                response_format="text"
            )
        
        spoken_text = transcription.strip()
        if not spoken_text:
            return "⚠️ Could not understand the audio. Please speak clearly.", ""

        # --- PHASE 2: Text-to-Text translation via Llama 3 ---
        system_instruction = (
            f"You are an expert real-time multilingual voice translator engine. "
            f"The user will provide text transcribed from an audio recording. "
            f"Analyze the text, detect its source language, and translate it into {target_language}. "
            f"Preserve the original meaning, cultural context, idioms, and tone exactly. "
            f"Provide ONLY the translated text as your final output. Do not write conversational notes or prefaces."
        )

        translation_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Translate this: {spoken_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
        )

        translated_text = translation_response.choices[0].message.content.strip()
        return spoken_text, translated_text

    except Exception as e:
        return f"System Error: {str(e)}", ""

# --- PHASE 3: Gradio UI Interface ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🎙️ PolyGlot AI - Universal Multilingual Voice Translator
        Record your speech in **any language** (English, Telugu, Hindi, etc.). The AI will automatically detect what language you spoke, transcribe it, and translate it into your target selection using **Whisper-Large-v3** and **Llama-3.3**!
        """
    )
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                sources=["microphone", "upload"], 
                type="filepath", 
                label="Speak Here (Any Language)"
            )
            
            lang_dropdown = gr.Dropdown(
                choices=["English", "Telugu (తెలుగు)", "Hindi (हिन्दी)", "Spanish (Español)", "French (Français)", "German (Deutsch)", "Japanese (日本語)", "Chinese (中文)", "Arabic (العربية)"],
                value="English",
                label="Target Language"
            )
            
            translate_btn = gr.Button("Translate Audio 🚀", variant="primary")
            
        with gr.Column():
            transcribed_output = gr.Textbox(label="1. Transcribed Text (Detected Original Language)", interactive=False)
            translated_output = gr.Textbox(label="2. Translated Output", interactive=False)

    translate_btn.click(
        fn=voice_translator_engine,
        inputs=[audio_input, lang_dropdown],
        outputs=[transcribed_output, translated_output]
    )

if __name__ == "__main__":
    demo.launch(server_port=5001)