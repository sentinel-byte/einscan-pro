import pytesseract
import cv2
import re
import numpy as np

class OCRReader:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def read_name(self, image_roi):
        """
        Lee el nombre del estudiante con preprocesamiento avanzado.
        """
        try:
            if image_roi is None or image_roi.size == 0:
                return ""

            # 1. Convertir a escala de grises si es necesario
            if len(image_roi.shape) == 3:
                gray = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY)
            else:
                gray = image_roi

            # 2. Re-escalar (Upscale) para mejorar OCR en textos pequeños
            gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            # 3. Eliminar ruido y mejorar contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
            # 4. Umbralización adaptativa para texto escrito a mano
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 31, 15)

            # 5. Configuración de Tesseract optimizada para nombres (alfabético)
            # lang='spa', psm 7 (una sola línea de texto)
            config = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNÑOPQRSTUVWXYZÁÉÍÓÚ "
            text = pytesseract.image_to_string(thresh, lang="spa", config=config)
            
            # 6. Limpieza
            cleaned_text = re.sub(r'[^A-ZÁÉÍÓÚÑ ]', '', text.upper())
            return " ".join(cleaned_text.split()) # Eliminar espacios extra
        except Exception as e:
            print(f"Error en OCR: {e}")
            return ""

