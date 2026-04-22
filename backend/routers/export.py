from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from datetime import datetime

from backend.database import get_db
from backend.models.exam import Exam
from backend.models.result import Result
from backend.models.student import Student

router = APIRouter()

@router.get("/excel/{exam_id}")
async def export_excel(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
        
    results = db.query(Result).filter(Result.exam_id == exam_id).all()
    
    if not results:
        raise HTTPException(status_code=400, detail="No hay resultados confirmados para exportar.")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultados"
    
    # Encabezados
    headers = ["Puesto", "Estudiante", "DNI", "Correctas", "Incorrectas", "Blancas", "Nota Final"]
    for col, text in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=text)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="CC0000", end_color="CC0000", fill_type="solid")
    
    # Ranking
    sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
    for i, r in enumerate(sorted_results, 1):
        student = db.query(Student).filter(Student.id == r.student_id).first()
        ws.cell(row=i+1, column=1, value=i)
        ws.cell(row=i+1, column=2, value=student.name if student else "Anonimo")
        ws.cell(row=i+1, column=3, value=student.dni if student else "-")
        ws.cell(row=i+1, column=4, value=r.correct)
        ws.cell(row=i+1, column=5, value=r.wrong)
        ws.cell(row=i+1, column=6, value=r.blank)
        ws.cell(row=i+1, column=7, value=r.score)

    path = f"data/exports/res_{exam_id}.xlsx"
    wb.save(path)
    return FileResponse(path, filename=f"Ranking_{exam.name}.xlsx")

@router.get("/pdf-boletas/{exam_id}")
async def export_pdf_boletas(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
        
    results = db.query(Result).filter(Result.exam_id == exam_id).all()
    if not results:
        raise HTTPException(status_code=400, detail="No hay resultados para generar boletas.")

    file_path = f"data/exports/boletas_{exam_id}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    w, h = A4
    
    for r in results:
        student = db.query(Student).filter(Student.id == r.student_id).first()
        
        # Diseño de la Boleta
        c.setFont("Helvetica-Bold", 18)
        c.setFillColorRGB(0.8, 0, 0)
        c.drawCentredString(w/2, h - 25*mm, "COLEGIO ALBERT EINSTEIN")
        
        c.setStrokeColorRGB(0.8, 0, 0)
        c.line(20*mm, h - 28*mm, w - 20*mm, h - 28*mm)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(w/2, h - 35*mm, "REPORTE INDIVIDUAL DE EVALUACIÓN")
        
        c.setFont("Helvetica", 10)
        c.drawString(25*mm, h - 50*mm, f"EXAMEN: {exam.name}")
        c.drawString(25*mm, h - 55*mm, f"MATERIA: {exam.subject}")
        c.drawString(25*mm, h - 60*mm, f"ESTUDIANTE: {student.name if student else 'S/N'}")
        c.drawString(25*mm, h - 65*mm, f"DNI: {student.dni if student else '-'}")
        
        # Resultados
        c.roundRect(25*mm, h - 95*mm, 160*mm, 25*mm, 3)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(35*mm, h - 85*mm, "PUNTAJE OBTENIDO:")
        c.drawRightString(175*mm, h - 85*mm, f"{r.score:.2f}")
        
        c.setFont("Helvetica", 10)
        c.drawString(35*mm, h - 110*mm, f"Correctas: {r.correct}  |  Incorrectas: {r.wrong}  |  Blancas: {r.blank}")
        
        c.showPage()
        
    c.save()
    return FileResponse(file_path, filename=f"Boletas_{exam.name}.pdf")

