import os
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, red, black, white, gray, lightgrey

class AnswerSheetGenerator:
    def __init__(self, output_path, layout_path, exam_id):
        self.output_path = output_path
        self.layout_path = layout_path
        self.exam_id = exam_id
        
        # Dimensiones A4 Landscape
        self.width, self.height = landscape(A4)
        self.dpi = 300
        
        self.galeno_red = HexColor("#CC0000")
        self.pink_bg = HexColor("#FFE8E8")
        
        self.layout = {
            "page_width_pt": self.width,
            "page_height_pt": self.height,
            "dpi": self.dpi,
            "timing_marks": {"top": [], "bottom": [], "left": [], "right": []},
            "answer_bubbles": {},
            "dni_bubbles": {},
            "aula_bubbles": {},
            "exam_type_bubbles": {},
            "name_field_bbox": {},
            "bubble_radius_pt": 4.5
        }

    def pos(self, x, y):
        """Coordenadas desde arriba-izquierda."""
        return x, self.height - y

    def draw_timing_marks(self, c):
        mark_w, mark_h = 5 * mm, 3 * mm
        margin = 10
        c.setFillColor(black)
        num_marks = 32
        for i in range(num_marks):
            x = margin + i * (self.width - 2 * margin) / (num_marks - 1)
            tx, ty = self.pos(x, margin)
            c.rect(tx - mark_w/2, ty - mark_h/2, mark_w, mark_h, fill=1)
            self.layout["timing_marks"]["top"].append([tx, ty])
            bx, by = self.pos(x, self.height - margin)
            c.rect(bx - mark_w/2, by - mark_h/2, mark_w, mark_h, fill=1)
            self.layout["timing_marks"]["bottom"].append([bx, by])

    def draw_identification_side(self, c):
        # MITAD IZQUIERDA (x: 0 a 420)
        start_x = 35
        
        # --- CABECERA IZQUIERDA ---
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(black)
        # Alineado verticalmente con Colegio Albert Einstein (35 + 5*mm)
        tx, ty = self.pos(start_x + 20*mm, 35 + 5*mm)
        c.drawString(tx, ty, "HOJA DE IDENTIFICACIÓN")

        # --- 1. DNI Y TIPO (PARTE SUPERIOR) ---
        dni_x, dni_y = 50, 85 + 10*mm
        c.setFont("Helvetica-Bold", 9)
        # Subimos el texto 10mm más (restando 10*mm en coordenadas top-down)
        tx_dni, ty_dni = self.pos(dni_x + 55, dni_y - 15 - 10*mm)
        c.drawCentredString(tx_dni, ty_dni, "DOCUMENTO NACIONAL")
        c.drawCentredString(tx_dni, ty_dni - 10, "DE IDENTIDAD (DNI)")
        
        for col in range(8):
            col_key = f"col_{col}"
            self.layout["dni_bubbles"][col_key] = {}
            wx, wy = self.pos(dni_x + col*15, dni_y - 10)
            c.setLineWidth(1)
            c.rect(wx, wy, 15, 12, stroke=1) # Casillas escritura
            
            for row in range(10):
                bx, by = dni_x + col*15 + 7.5, dni_y + row*14 + 13
                rbx, rby = self.pos(bx, by)
                c.setStrokeColor(black)
                c.circle(rbx, rby, 5, stroke=1, fill=0)
                c.setFont("Helvetica", 6)
                c.drawCentredString(rbx, rby - 2, str(row))
                self.layout["dni_bubbles"][col_key][str(row)] = [rbx, rby]

        # TIPO DE PRUEBA (al lado del DNI)
        type_x, type_y = 200, 85
        c.setFont("Helvetica-Bold", 9)
        tx_t, ty_t = self.pos(type_x + 10, type_y - 15)
        c.drawCentredString(tx_t, ty_t, "TIPO")
        for i, t in enumerate(["P", "Q", "R", "S", "T"]):
            bx, by = type_x + 10, type_y + i*25 + 10
            rbx, rby = self.pos(bx, by)
            c.circle(rbx, rby, 7.5, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(rbx, rby - 3, t)
            self.layout["exam_type_bubbles"][t] = [rbx, rby]

        # --- 1.5 INSTRUCCIONES (DERECHA DE TIPO) ---
        instr_x = 265
        # Alineado al nivel de TIPO (type_y - 15)
        tx_ins, ty_ins = self.pos(instr_x + 5, 85 - 15)
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(tx_ins, ty_ins, "INSTRUCCIONES")
        c.setFont("Helvetica", 6.5)
        lines = [
            "• No arrugue ni maltrate esta",
            "  hoja de respuestas.",
            "• No use plumón ni lapicero.",
            "  Rellene el círculo completamente",
            "  y sólo una alternativa por pregunta.",
            "• En caso de error, borre con",
            "  cuidado y rellene de nuevo.",
            "• USE SOLO LÁPIZ N.° 2"
        ]
        for i, line in enumerate(lines):
            # Posicionamos las líneas debajo del título alineado
            lx, ly = self.pos(instr_x + 5, 85 + i*11)
            c.drawString(lx, ly, line)

        # --- 2. CAMPOS DE ESCRITURA (DEBAJO DEL DNI) ---
        fields_y_start = 295
        labels = [
            "APELLIDO PATERNO", 
            "APELLIDO MATERNO", 
            "NOMBRES", 
            "ESCUELA PROFESIONAL / AULA"
        ]
        
        box_w = 350 
        box_h = 20  
        
        c.setFont("Helvetica-Bold", 9)
        for i, label in enumerate(labels):
            y = fields_y_start + (i * 42)
            lx, ly = self.pos(start_x, y)
            c.drawString(lx, ly, label)
            c.setLineWidth(1.2)
            c.rect(lx, ly - 24, box_w, box_h, stroke=1)
            self.layout["name_field_bbox"][label] = [lx, ly - 24, box_w, box_h]

        # FIRMA DEL POSTULANTE
        lx, ly = self.pos(start_x, 465)
        c.drawString(lx, ly, "FIRMA DEL POSTULANTE")
        c.rect(lx, ly - 75, box_w, 70, stroke=1)

    def draw_answer_side(self, c):
        # MITAD DERECHA
        start_x = self.width / 2 + 35
        
        # --- CABECERA DERECHA ---
        # Colegio Albert Einstein (Ajustado: +1.5cm a la derecha)
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(self.galeno_red)
        tx_ae, ty_ae = self.pos(start_x + 15*mm, 35 + 5*mm)
        c.drawString(tx_ae, ty_ae, "COLEGIO ALBERT EINSTEIN")

        # Hoja de Respuestas
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(black)
        tx, ty = self.pos(start_x + 30*mm, 45 + 10*mm)
        c.drawString(tx, ty, "HOJA DE RESPUESTAS")

        q_y_start = 100
        for block in range(2):
            bx_offset = start_x + (block * 185)
            for q_idx in range(30):
                q_num = (block * 30) + q_idx + 1
                y = q_y_start + (q_idx * 14)
                rx, ry = self.pos(bx_offset, y)
                if q_idx % 2 == 1:
                    c.setFillColor(self.pink_bg)
                    c.rect(rx - 5, ry - 3, 175, 14, stroke=0, fill=1)
                c.setFillColor(black)
                c.setFont("Helvetica-Bold", 9)
                c.drawRightString(rx + 15, ry, str(q_num))
                self.layout["answer_bubbles"][str(q_num)] = {}
                for i, opt in enumerate(["A", "B", "C", "D", "E"]):
                    bubble_x = rx + 35 + (i * 26)
                    c.setStrokeColor(black)
                    c.circle(bubble_x, ry + 3, 5.5, stroke=1, fill=0)
                    c.setFont("Helvetica-Bold", 7)
                    c.drawCentredString(bubble_x, ry + 1, opt)
                    self.layout["answer_bubbles"][str(q_num)][opt] = [bubble_x, ry + 3]

    def generate(self, num_questions=60, options=5):
        c = canvas.Canvas(self.output_path, pagesize=landscape(A4))
        self.draw_timing_marks(c)
        
        # Línea divisoria central
        c.setDash(3, 3)
        c.setStrokeColor(gray)
        c.line(self.width/2, 30, self.width/2, self.height - 30)
        c.setDash(1, 0)
        
        self.draw_identification_side(c)
        self.draw_answer_side(c)
        
        c.save()
        with open(self.layout_path, 'w') as f:
            json.dump(self.layout, f, indent=2)
        return self.output_path
