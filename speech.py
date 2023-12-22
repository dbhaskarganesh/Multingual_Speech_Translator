# speech.py
from googletrans import Translator

def translate_text(text, target_language):
    translator = Translator()
    translation = translator.translate(text, src='auto', dest=target_language)
    return translation.text
