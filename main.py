from flask import Flask, render_template, request, flash
from transformers import pipeline
from googletrans import Translator
from gtts import gTTS
import os
from time import time

app = Flask(__name__)
app.secret_key="cheech"

# Initialize the text generator and translator
generator = pipeline('text-generation', model="EleutherAI/gpt-neo-1.3B") #Use 1.3B for more coherent sentences, use distilbertGPT2 for faster.
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/langen')
def about():
    return render_template('langen.html')

@app.route('/savedwords')
def contact():
    return render_template('savedwords.html')

@app.route('/ourteam')
def post():
    return render_template('ourteam.html')

# In your Flask route
@app.route('/submit', methods=['POST'])
def submit():
    try:
        prompt = request.form['prompt']
        language_input = request.form['language']
        word_count = request.form['wordCount']
        language_code = language_input

        # Generate text based on the prompt
        stop_token = "."
        generated_text = generator(prompt, min_length=int(word_count), max_length=int(word_count), do_sample=True, temperature=0.75, top_p=0.9, top_k=50, truncation=True)
        generated_text = generated_text[0]['generated_text']
        if stop_token in generated_text:
            generated_text = generated_text[:generated_text.rfind(stop_token) + 1]

        # TTS for generated text
        english_file_name = 'audio.mp3'
        tts = gTTS(generated_text, lang='en')
        tts.save(os.path.join('LanGen/static/assets/audio', english_file_name))

        # Translate the generated text
        def translate_text(text: str, src_lang: str = 'en', dest_lang: str = language_code) -> str:
            translated = translator.translate(text, src=src_lang, dest=dest_lang)
            return translated.text

        translation = translate_text(generated_text, src_lang='en', dest_lang = language_code)

        # TTS for translated text
        translated_file_name = 'translated_audio.mp3'
        tts = gTTS(translation, lang=language_code)
        tts.save(os.path.join('LanGen/static/assets/audio', translated_file_name))

        current_time = int(time())

        return render_template('langen.html', original_text=generated_text, translated_text=translation, audio_file=english_file_name, translated_audio_file=translated_file_name, time = current_time)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, port = 5000)