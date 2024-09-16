import re
import os
from pathlib import Path
from striprtf.striprtf import rtf_to_text
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
load_dotenv()

file_name = os.getenv('MR_FILE_NAME')

def get_translator():
    translator = GoogleTranslator(source='mr', target='en')
    return translator

def translate(file_name):
    if "." not in file_name or file_name.endswith("."):
        raise HTTPException(
            status_code=422,
            detail="Please provide a valid filename with .rtf extension."
        )
    
    static_dir = Path(__file__).resolve().parent.parent / "static" / "original_marathi_files"
    file_path = static_dir / file_name
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File '{file_name}' not found in the source directory. Please check the file name."
        )
    
    try:
        marathi_text_from_file = read_marathi_text_file(file_path)
        paragraphs = split_text_into_paragraphs(marathi_text_from_file)
        translated_text_in_english = translate_using_translator(paragraphs)
        print('============', translated_text_in_english)
        translated_file_name = save_translated_content_to_file(translated_text_in_english, file_name)
        return JSONResponse(
                    status_code=200,
                    content={"message": f'File "{translated_file_name}" saved successfully to the destination directory.'}
                )    
    except Exception as E:
            return E

def translate_using_translator(paragraphs):
    try:
        translator = get_translator()
        english_text_by_google = ''
        for paragraph in paragraphs:
            sentence = paragraph.split('.')
            for each_sentence in sentence:
                split_parts = split_text_by_quotes(each_sentence)
                if len(split_parts) > 1:
                    for s_para in split_parts:
                        if s_para:
                            result = translator.translate(s_para)
                            if result:
                                english_text_by_google = english_text_by_google + result + ' '
                    english_text_by_google = english_text_by_google + '. '
                else:
                    if split_parts:
                        result = translator.translate(split_parts[0])
                        if result:
                            english_text_by_google = english_text_by_google + result + '. '
            english_text_by_google = english_text_by_google + '\n'
        english_text_by_google = english_text_by_google.replace('..', '.')
        formatted_text = get_formatted_text(english_text_by_google)
        return formatted_text
    except Exception as E:
        return E

def get_formatted_text(text):
    formatted_text = text.split('\n')
    formatted_text_final = ''
    for text in formatted_text:
        formatted_text_final = formatted_text_final + '\t' + text + '\n'
    return formatted_text_final

def read_marathi_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        rtf_content = file.read()  # Read the RTF file content
    plain_text = rtf_to_text(rtf_content)  # Convert RTF to plain text
    return plain_text

def split_text_into_paragraphs(text):
    paragraphs = text.split('\n')
    return [p.strip() for p in paragraphs if p.strip()]

def split_text_by_quotes(text):
    # Use regex to split text by quotes and keep both quoted and non-quoted parts
    parts = re.split(r"([‘’].+?[‘’])", text)

    # Strip any leading/trailing whitespace from each part
    parts = [part.strip() for part in parts if part.strip()]

    return parts

def save_translated_content_to_file(translated_text, file_name):
    destination_dir = Path(__file__).resolve().parent.parent / "static" / "en_translated_files"
    try:
        translated_file_name = f"translated_en_{file_name.split('.')[0]}.txt"
        file_path = destination_dir / translated_file_name
        with open(file_path, "w", encoding="utf-8") as textfile:
            textfile.write(translated_text)
        return translated_file_name
    except Exception as E:
        return E
    
translate(file_name=file_name)