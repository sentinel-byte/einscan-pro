import cv2
import numpy as np
import json
import os

class OMRPipeline:
    def __init__(self, layout_path):
        with open(layout_path, 'r') as f:
            self.layout = json.load(f)
            
        self.dpi = self.layout.get("dpi", 300)
        self.pt_to_px = self.dpi / 72.0
        self.target_w = int(self.layout["page_width_pt"] * self.pt_to_px)
        self.target_h = int(self.layout["page_height_pt"] * self.pt_to_px)
        self.bubble_r = int(self.layout.get("bubble_radius_pt", 4.5) * self.pt_to_px)

    def preprocess(self, img):
        """Preprocesamiento para mejorar el contraste de las burbujas."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # Normalizar iluminación
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(gray)
        return cv2.GaussianBlur(contrast, (5, 5), 0)

    def find_corners(self, img):
        """Detecta las 4 esquinas usando las marcas negras del PDF excelente."""
        thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 31, 10)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        marks = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            aspect = w / float(h)
            # Marcas de 5x3mm aprox
            if 0.8 < aspect < 3.0 and 400 < area < 10000:
                marks.append([x + w//2, y + h//2])
        
        if len(marks) < 4: return None
        
        marks = np.array(marks)
        # Identificar esquinas extremas
        tl = marks[np.argmin(marks[:,0] + marks[:,1])]
        tr = marks[np.argmax(marks[:,0] - marks[:,1])]
        bl = marks[np.argmin(marks[:,0] - marks[:,1])]
        br = marks[np.argmax(marks[:,0] + marks[:,1])]
        
        return np.float32([tl, tr, bl, br])

    def get_darkness(self, img, center):
        """Calcula qué tan llena está una burbuja (0 a 1)."""
        x, y = int(center[0] * self.pt_to_px), int(center[1] * self.pt_to_px)
        r = int(self.bubble_r * 0.8) # Margen interno
        
        roi = img[y-r:y+r, x-r:x+r]
        if roi.size == 0: return 0
        
        # Máscara circular
        mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(mask, (r, r), r-1, 255, -1)
        
        # Promedio de oscuridad
        mean = cv2.mean(roi, mask=mask)[0]
        return 1.0 - (mean / 255.0)

    def process_image(self, path):
        img = cv2.imread(path)
        if img is None: return {"error": "Imagen ilegible"}
        
        # 1. Redimensionar si es gigante para no agotar la RAM de Render
        if img.shape[1] > 2500:
            scale = 2000 / float(img.shape[1])
            img = cv2.resize(img, None, fx=scale, fy=scale)
            
        pre = self.preprocess(img)
        corners = self.find_corners(pre)
        
        if corners is None:
            return {"error": "No se detectan las marcas de los bordes. Asegura buena luz."}
            
        # 2. Corregir perspectiva
        margin = 10 * self.pt_to_px
        dst = np.float32([
            [margin, margin], [self.target_w - margin, margin],
            [margin, self.target_h - margin], [self.target_w - margin, self.target_h - margin]
        ])
        M = cv2.getPerspectiveTransform(corners, dst)
        warped = cv2.warpPerspective(pre, M, (self.target_w, self.target_h))
        
        # 3. Extraer Datos
        res = {"answers": {}, "dni": "", "exam_type": "P", "name_rois": {}}
        
        # DNI (8 col)
        for col in range(8):
            best_val, best_d = None, 0.40
            for digit, pt in self.layout["dni_bubbles"][f"col_{col}"].items():
                d = self.get_darkness(warped, pt)
                if d > best_d: best_d, best_val = d, digit
            res["dni"] += best_val if best_val else "?"
            
        # Tipo
        bt, btd = "P", 0.40
        for t, pt in self.layout["exam_type_bubbles"].items():
            d = self.get_darkness(warped, pt)
            if d > btd: btd, bt = d, t
        res["exam_type"] = bt
        
        # Respuestas (60)
        for q, opts in self.layout["answer_bubbles"].items():
            marked = []
            for letter, pt in opts.items():
                if self.get_darkness(warped, pt) > 0.45: marked.append(letter)
            
            if not marked: res["answers"][q] = {"answer": None, "status": "blank"}
            elif len(marked) == 1: res["answers"][q] = {"answer": marked[0], "status": "ok"}
            else: res["answers"][q] = {"answer": "".join(marked), "status": "double"}
            
        # 4. ROIs para OCR
        for field in ["NOMBRES", "APELLIDO PATERNO", "APELLIDO MATERNO"]:
            bbox = self.layout["name_field_bbox"].get(field)
            if bbox:
                x, y, w, h = [int(v * self.pt_to_px) for v in bbox]
                res["name_rois"][field] = warped[y+2:y+h-2, x+2:x+w-2]
                
        return res
