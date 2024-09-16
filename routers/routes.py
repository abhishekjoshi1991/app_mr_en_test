from fastapi import APIRouter, Query, UploadFile, File
from services.service import translate

router = APIRouter(prefix="/api")

@router.post("/translate_file_from_mr_to_en")
# async def translate_file_from_marathi_to_english(
def translate_file_from_marathi_to_english(
        file: UploadFile = File(..., description="A file containing Marathi text. Supported formats: .docx, .txt, .rtf.")):
    # file_content = await file.read()
    # return translate(file, file_content, file.filename)
    return translate(file)