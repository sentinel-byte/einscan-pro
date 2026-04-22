import os
import google.generativeai as genai
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

class GeminiFallback:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.enabled = False

    async def review_ambiguous_question(self, image_roi, question_num, letters):
        """
        Envía un recorte de la pregunta a Gemini para decidir qué burbuja está marcada.
        image_roi: numpy array (recorte de la fila de burbujas)
        """
        if not self.enabled:
            return None

        # Convertir numpy ROI a bytes para PIL
        from PIL import Image
        import cv2
        
        # Convertir BGR a RGB si es necesario
        image_rgb = cv2.cvtColor(image_roi, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(image_rgb)
        
        prompt = f"""
        Esta es una fila de burbujas de una ficha de respuestas OMR (Pregunta {question_num}).
        Las opciones son: {', '.join(letters)}.
        ¿Qué burbuja(s) están claramente marcadas o rellenas por el estudiante?
        - Si ninguna está marcada, responde: BLANK.
        - Si solo una está marcada, responde solo la LETRA.
        - Si hay más de una marcada, responde las LETRAS juntas (ej: AC).
        Responde ÚNICAMENTE con la letra o letras o la palabra BLANK.
        """

        try:
            response = self.model.generate_content([prompt, pil_img])
            decision = response.text.strip().upper()
            return decision if decision != "BLANK" else None
        except Exception as e:
            print(f"Error en Gemini Fallback: {e}")
            return None
