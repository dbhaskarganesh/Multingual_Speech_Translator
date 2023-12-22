# app.py
from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from googletrans import Translator
import speech_recognition as sr
import mysql.connector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'wav'}

# Define the target languages
LANGUAGES = {
    'hindi': 'Hindi',
    'tamil': 'Tamil',
    'telugu': 'Telugu',
}

# Configure MySQL database connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Charan@2004',
    database='speech'
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)

        try:
            recognized_text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            recognized_text = "Speech recognition could not understand the audio."
        except sr.RequestError as e:
            recognized_text = f"Could not request results from Google Speech Recognition service; {e}"

        # Translate the recognized text to all target languages
        translations = translate_to_languages(recognized_text)

        # Save all translations to the MySQL database
        save_translations_to_database(recognized_text, translations)

        return render_template('result.html', recognized_text=recognized_text, translations=translations)

    return redirect(request.url)

def translate_to_languages(text):
    translator = Translator()
    translations = {}
    for language_code, language_name in LANGUAGES.items():
        translation = translator.translate(text, src='auto', dest=language_code)
        translations[language_name] = translation.text
    return translations

def save_translations_to_database(recognized_text, translations):
    cursor = db.cursor()
    insert_query = "INSERT INTO translation_results (recognized_text, hindi_translation, tamil_translation, telugu_translation) VALUES (%s, %s, %s, %s)"
    values = (recognized_text, translations['Hindi'], translations['Tamil'], translations['Telugu'])
    cursor.execute(insert_query, values)
    db.commit()
    cursor.close()

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
