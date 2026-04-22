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
        self.page_h_pt = self.layout["page_height_pt"]
        self.target_w = int(self.layout["page_width_pt"] * self.pt_to_px)
        self.target_h = int(self.page_h_pt * self.pt_to_px)
        self.bubble_r = int(self.layout.get("bubble_radius_pt", 4.5) * self.pt_to_px)

    def preprocess(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(10,10))
        contrast = clahe.apply(gray)
        return cv2.GaussianBlur(contrast, (5, 5), 0)

    def find_corners(self, img):
        """Detecta las marcas negras del PDF excelente para alinear la foto."""
        thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 31, 10)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        marks = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            aspect = w / float(h)
            if 0.8 < aspect < 3.0 and 400 < area < 10000:
                marks.append([x + w//2, y + h//2])
        
        if len(marks) < 4: return None
        marks = np.array(marks)
        tl = marks[np.argmin(marks[:,0] + marks[:,1])]
        tr = marks[np.argmax(marks[:,0] - marks[:,1])]
        bl = marks[np.argmin(marks[:,0] - marks[:,1])]
        br = marks[np.argmax(marks[:,0] + marks[:,1])]
        return np.float32([tl, tr, bl, br])

    def get_darkness(self, img, pt):
        """
        Calcula la oscuridad. 
        IMPORTANTE: Convierte coordenadas de ReportLab (bottom-up) a Imagen (top-down).
        """
        x_pt, y_pt = pt[0], pt[1]
        # Inversión de coordenadas: y_top_down = altura_total - y_bottom_up
        y_td = self.page_h_pt - y_pt
        
        ix, iy = int(x_pt * self.pt_to_px), int(y_td * self.pt_to_px)
        r = int(self.bubble_r * 0.8)
        
        roi = img[iy-r:iy+r, ix-r:ix+r]
        if roi.size == 0: return 0
        
        mask = np.zeros(roi.shape, dtype=np.uint8)
        cv2.circle(mask, (r, r), r-1, 255, -1)
        mean = cv2.mean(roi, mask=mask)[0]
        return 1.0 - (mean / 255.0)

    def process_image(self, path):
        img = cv2.imread(path)
        if img is None: return {"error": "No se puede leer la foto"}
        if img.shape[1] > 2500: # Optimización de RAM para Render
            scale = 2000 / float(img.shape[1])
            img = cv2.resize(img, None, fx=scale, fy=scale)
            
        pre = self.preprocess(img)
        corners = self.find_corners(pre)
        if corners is None: return {"error": "No se ven las marcas negras de los bordes. Mejora la luz."}
            
        margin_px = 10 * self.pt_to_px
        dst = np.float32([
            [margin_px, margin_px], [self.target_w - margin_px, margin_px],
            [margin_px, self.target_h - margin_px], [self.target_w - margin_px, self.target_h - margin_px]
        ])
        M = cv2.getPerspectiveTransform(corners, dst)
        warped = cv2.warpPerspective(pre, M, (self.target_w, self.target_h))
        
        res = {"answers": {}, "dni": "", "exam_type": "P"}
        
        # 1. DNI
        for col in range(8):
            best_val, max_d = None, 0.40
            for digit, pt in self.layout["dni_bubbles"][f"col_{col}"].items():
                d = self.get_darkness(warped, pt)
                if d > max_d: max_d, best_val = d, digit
            res["dni"] += best_val if best_val else "?"
            
        # 2. TIPO
        bt, mtd = "P", 0.40
        for t, pt in self.layout["exam_type_bubbles"].items():
            d = self.get_darkness(warped, pt)
            if d > mtd: mtd, bt = d, t
        res["exam_type"] = bt
        
        # 3. RESPUESTAS (60)
        for q, opts in self.layout["answer_bubbles"].items():
            marked = []
            for letter, pt in opts.items():
                if self.get_darkness(warped, pt) > 0.45: marked.append(letter)
            if not marked: res["answers"][q] = {"answer": None, "status": "blank"}
            elif len(marked) == 1: res["answers"][q] = {"answer": marked[0], "status": "ok"}
            else: res["answers"][q] = {"answer": "".join(marked), "status": "double"}
            
        return res
