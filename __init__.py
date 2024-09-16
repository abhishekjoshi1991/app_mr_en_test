from deep_translator import GoogleTranslator

def get_translator():
    translator = GoogleTranslator(source='mr', target='en')
    return translator