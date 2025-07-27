import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from PIL import Image
from pdf2image import convert_from_path
import os

def extract_text_from_scanned_pdf(file_path, dpi=300):
    ext = os.path.splitext(file_path)[1].lower()
    extracted_text = ""

    try:
        if ext in [".jpg", ".jpeg", ".png"]:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image, lang='eng')

        elif ext == ".pdf":
            pages = convert_from_path(file_path, dpi=dpi)
            for i, page in enumerate(pages):
                extracted_text += f"\n--- Page {i+1} ---\n"
                extracted_text += pytesseract.image_to_string(page, lang='eng')

        else:
            raise ValueError("Unsupported file type.")

    except Exception as e:
        print(f" OCR Failed: {e}")

    return extracted_text
