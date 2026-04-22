import cv2
import numpy as np
import json
import os
from PIL import Image

class OMRPipeline:
    def __init__(self, layout_path):
        with open(layout_path, 'r') as f:
            self.layout = json.load(f)
            
        self.pt_to_px = self.layout["dpi"] / 72.0
        self.target_w = int(self.layout["page_width_pt"] * self.pt_to_px)
        self.target_h = int(self.layout["page_height_pt"] * self.pt_to_px)
        self.bubble_radius = int(self.layout["bubble_radius_pt"] * self.pt_to_px)

    def preprocess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # CLAHE para mejorar contraste local (útil para fotos con sombras)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(gray)
        blurred = cv2.GaussianBlur(contrast, (3, 3), 0)
        return blurred

    def get_perspective_transform(self, image):
        """Detecta marcas de tiempo y calcula la transformación."""
        # Umbralización adaptativa para detectar las marcas negras
        thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar rectángulos que parezcan marcas de tiempo (4x3 mm aprox)
        marks = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h)
            area = cv2.contourArea(cnt)
            
            # Ajustar estos valores según la escala de la imagen
            if 0.8 < aspect_ratio < 2.0 and area > 50:
                marks.append([x + w//2, y + h//2])
        
        if len(marks) < 4:
            return None, 0

        # Encontrar las 4 esquinas más extremas entre las marcas detectadas
        marks = np.array(marks)
        top_left = marks[np.argmin(marks[:,0] + marks[:,1])]
        top_right = marks[np.argmax(marks[:,0] - marks[:,1])]
        bot_left = marks[np.argmin(marks[:,0] - marks[:,1])]
        bot_right = marks[np.argmax(marks[:,0] + marks[:,1])]
        
        src_pts = np.float32([top_left, top_right, bot_left, bot_right])
        
        # Puntos de destino basados en el layout (en píxeles)
        # Usamos la primera y última marca de tiempo definida en el layout para mayor precisión
        tl_layout = np.array(self.layout["timing_marks"]["top"][0]) * self.pt_to_px
        tr_layout = np.array(self.layout["timing_marks"]["top"][-1]) * self.pt_to_px
        bl_layout = np.array(self.layout["timing_marks"]["bottom"][0]) * self.pt_to_px
        br_layout = np.array(self.layout["timing_marks"]["bottom"][-1]) * self.pt_to_px
        
        dst_pts = np.float32([tl_layout, tr_layout, bl_layout, br_layout])
        
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        return M, 1.0

    def process_bubble(self, image, center_pt):
        cx, cy = int(center_pt[0] * self.pt_to_px), int(center_pt[1] * self.pt_to_px)
        r = self.bubble_radius
        
        # Extraer ROI
        roi = image[cy-r:cy+r, cx-r:cx+r]
        if roi.size == 0: return 0, "error"
        
        # Umbral de Otsu para separar papel de marca
        _, thresh = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Calcular ratio de llenado (píxeles negros / total área de la burbuja)
        # Creamos una máscara circular para solo contar lo de adentro
        mask = np.zeros_like(thresh)
        cv2.circle(mask, (r, r), r-1, 255, -1)
        filled_pixels = cv2.countNonZero(cv2.bitwise_and(thresh, mask))
        total_pixels = cv2.countNonZero(mask)
        
        fill_ratio = filled_pixels / float(total_pixels)
        
        status = "empty"
        if fill_ratio > 0.55: status = "filled"
        elif fill_ratio > 0.25: status = "ambiguous"
        
        return fill_ratio, status

    def process_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None: return None
        
        processed = self.preprocess(img)
        M, quality = self.get_perspective_transform(processed)
        
        if M is None:
            return {"error": "No se detectaron marcas de tiempo", "warp_quality": 0}
            
        # Corregir perspectiva
        warped = cv2.warpPerspective(processed, M, (self.target_w, self.target_h))
        
        results = {
            "answers": {},
            "dni": "",
            "exam_type": "",
            "warp_quality": quality,
            "ambiguous_count": 0
        }
        
        # 1. Respuestas
        for q_num, opts in self.layout["answer_bubbles"].items():
            q_res = []
            for letter, center in opts.items():
                ratio, status = self.process_bubble(warped, center)
                if status == "filled": q_res.append(letter)
                elif status == "ambiguous": results["ambiguous_count"] += 1
            
            if len(q_res) == 0: results["answers"][q_num] = {"answer": None, "status": "blank"}
            elif len(q_res) == 1: results["answers"][q_num] = {"answer": q_res[0], "status": "ok"}
            else: results["answers"][q_num] = {"answer": "".join(q_res), "status": "double_mark"}

        # 2. DNI
        dni_str = ""
        for col in range(8):
            col_key = f"col_{col}"
            best_digit = None
            max_ratio = 0.55
            for digit, center in self.layout["dni_bubbles"][col_key].items():
                ratio, status = self.process_bubble(warped, center)
                if ratio > max_ratio:
                    max_ratio = ratio
                    best_digit = digit
            dni_str += best_digit if best_digit else "?"
        results["dni"] = dni_str

        # 3. Tipo de examen
        for t, center in self.layout["exam_type_bubbles"].items():
            ratio, status = self.process_bubble(warped, center)
            if status == "filled":
                results["exam_type"] = t
                break
                
        return results
