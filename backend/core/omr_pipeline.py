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
        """Preprocesamiento robusto para fotos."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(12,12))
        contrast = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(contrast, None, 10, 7, 21)
        return denoised

    def detect_timing_marks(self, image):
        thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 21, 10)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        marks = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h)
            area = cv2.contourArea(cnt)
            if 1.0 < aspect_ratio < 2.5 and 500 < area < 5000:
                marks.append([x + w//2, y + h//2])
        return np.array(marks)

    def get_perspective_transform(self, image):
        marks = self.detect_timing_marks(image)
        if len(marks) < 4: return None, 0
        top_left = marks[np.argmin(marks[:,0] + marks[:,1])]
        top_right = marks[np.argmax(marks[:,0] - marks[:,1])]
        bot_left = marks[np.argmin(marks[:,0] - marks[:,1])]
        bot_right = marks[np.argmax(marks[:,0] + marks[:,1])]
        src_pts = np.float32([top_left, top_right, bot_left, bot_right])
        margin_px = 10 * self.pt_to_px
        dst_pts = np.float32([
            [margin_px, margin_px],
            [self.target_w - margin_px, margin_px],
            [margin_px, self.target_h - margin_px],
            [self.target_w - margin_px, self.target_h - margin_px]
        ])
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        quality = min(len(marks) / 60.0, 1.0)
        return M, quality

    def process_bubble(self, image, center_pt):
        cx, cy = int(center_pt[0] * self.pt_to_px), int(center_pt[1] * self.pt_to_px)
        r = int(self.bubble_radius * 0.9)
        roi = image[cy-r:cy+r, cx-r:cx+r]
        if roi.size == 0: return 0, "error"
        mask = np.zeros((2*r, 2*r), dtype=np.uint8)
        cv2.circle(mask, (r, r), r-1, 255, -1)
        mean_val = cv2.mean(roi, mask=mask)[0]
        darkness = 1.0 - (mean_val / 255.0)
        status = "empty"
        if darkness > 0.45: status = "filled"
        elif darkness > 0.20: status = "ambiguous"
        return darkness, status

    def extract_field_roi(self, warped_image, field_name):
        """Extrae el recorte de un campo de escritura (como Nombres)."""
        bbox = self.layout["name_field_bbox"].get(field_name)
        if not bbox: return None
        x, y, w, h = [int(v * self.pt_to_px) for v in bbox]
        # Añadir un pequeño margen interno para no tomar los bordes del recuadro
        roi = warped_image[y+2:y+h-2, x+2:x+w-2]
        return roi

    def process_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None: return {"error": "No se pudo leer la imagen"}
        preprocessed = self.preprocess(img)
        M, quality = self.get_perspective_transform(preprocessed)
        if M is None or quality < 0.1:
            return {"error": "No se detectaron marcas de sincronización", "warp_quality": quality}
        warped = cv2.warpPerspective(preprocessed, M, (self.target_w, self.target_h))
        
        results = {"answers": {}, "dni": "", "exam_type": "P", "warp_quality": quality, "name_rois": {}}
        
        # DNI
        dni_str = ""
        for col in range(8):
            col_key = f"col_{col}"
            best_digit, max_darkness = None, 0.45
            for digit, center in self.layout["dni_bubbles"][col_key].items():
                darkness, status = self.process_bubble(warped, center)
                if darkness > max_darkness: max_darkness, best_digit = darkness, digit
            dni_str += best_digit if best_digit else "?"
        results["dni"] = dni_str

        # Tipo
        best_type, max_type_dark = "P", 0.45
        for t, center in self.layout["exam_type_bubbles"].items():
            darkness, _ = self.process_bubble(warped, center)
            if darkness > max_type_dark: max_type_dark, best_type = darkness, t
        results["exam_type"] = best_type

        # Respuestas
        for q_num, opts in self.layout["answer_bubbles"].items():
            marked = []
            for letter, center in opts.items():
                darkness, status = self.process_bubble(warped, center)
                if status == "filled": marked.append(letter)
            if len(marked) == 0: results["answers"][q_num] = {"answer": None, "status": "blank"}
            elif len(marked) == 1: results["answers"][q_num] = {"answer": marked[0], "status": "ok"}
            else: results["answers"][q_num] = {"answer": "".join(marked), "status": "double_mark"}

        # Extraer ROIs de nombres para el OCR
        for field in ["NOMBRES", "APELLIDO PATERNO", "APELLIDO MATERNO"]:
            roi = self.extract_field_roi(warped, field)
            if roi is not None:
                results["name_rois"][field] = roi
        
        return results

