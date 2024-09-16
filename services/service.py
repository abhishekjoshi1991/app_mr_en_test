import re
from pathlib import Path
from striprtf.striprtf import rtf_to_text
from __init__ import get_translator
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from docx import Document
from app_logging.logger import Logger

logger = Logger().get_logger(__name__)

# def translate(file, file_content, file_name):
def translate(file):
    file_content = file.file.read()
    if not (file.filename.endswith(".rtf") or file.filename.endswith(".docx") or file.filename.endswith(".txt")):
        logger.warning(f"Unsupported file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Please provide a valid file with the correct extension. Supported formats are .rtf, .docx, and .txt.")
    try:
        if file.filename.endswith(".rtf"):
            marathi_text_from_file = read_marathi_text_file(file_content=file_content)
        elif file.filename.endswith(".docx"):
            marathi_text_from_file = read_docx(file)
        else:
            marathi_text_from_file = file_content.decode("utf-8")

        paragraphs = split_text_into_paragraphs(marathi_text_from_file)
        translated_text_in_english = translate_using_translator(paragraphs)
        print('============', translated_text_in_english)
        english_bytes = BytesIO(translated_text_in_english.encode("utf-8"))
        translated_filename = f"translated_EN_{file.filename.split('.')[0]}" if file.filename else "translated_file.txt"

        return StreamingResponse(
            english_bytes, 
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={translated_filename}"}
        )
    except Exception as e:
        logger.error(f"An error occurred during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

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
    except Exception as e:
        logger.error(f"An error occurred during translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def get_formatted_text(text):
    formatted_text = text.split('\n')
    formatted_text_final = ''
    for text in formatted_text:
        formatted_text_final = formatted_text_final + '\t' + text + '\n'
    return formatted_text_final

def read_docx(file):
    try:
        doc = Document(file.file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return ' '.join(full_text)
    except Exception as e:
        logger.error(f"An error occurred while reading DOCX file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def read_marathi_text_file(file_content):
    try:
        plain_text = rtf_to_text(file_content.decode("utf-8"))  # Convert RTF to plain text
        logger.info("RTF converted to plain text successfully")

        return plain_text
    except Exception as e:
        logger.error(f"An error occurred while converting RTF file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def split_text_into_paragraphs(text):
    paragraphs = text.split('\n')
    return [p.strip() for p in paragraphs if p.strip()]

def split_text_by_quotes(text):
    # Use regex to split text by quotes and keep both quoted and non-quoted parts
    parts = re.split(r"([‘’].+?[‘’])", text)

    # Strip any leading/trailing whitespace from each part
    parts = [part.strip() for part in parts if part.strip()]

    return parts
