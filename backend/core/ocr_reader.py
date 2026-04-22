import pytesseract
import cv2
import re

class OCRReader:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def read_name(self, image_roi):
        """
        Lee el nombre del estudiante desde el ROI del campo de nombre.
        """
        try:
            # Preprocesamiento para OCR
            gray = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY) if len(image_roi.shape) == 3 else image_roi
            # Umbralización para texto negro sobre fondo blanco
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Configuración de Pytesseract: psm 7 es para una sola línea de texto
            config = "--psm 7"
            text = pytesseract.image_to_string(thresh, lang="spa", config=config)
            
            # Limpieza básica
            cleaned_text = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', text)
            return cleaned_text.strip()
        except Exception as e:
            print(f"Error en OCR: {e}")
            return ""
