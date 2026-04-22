from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import time

from backend.database import get_db
from backend.models.exam import Exam
from backend.core.pdf_generator import AnswerSheetGenerator

router = APIRouter()

@router.post("/generate/{exam_id}")
async def generate_pdf(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    
    # Ruta base del proyecto
    base_dir = os.getcwd()
    filename = f"ficha_examen_{exam_id}.pdf"
    layout_filename = f"{exam_id}_layout.json"
    
    # Asegurar que la carpeta data/sheets existe
    sheets_dir = os.path.join(base_dir, "data", "sheets")
    if not os.path.exists(sheets_dir):
        os.makedirs(sheets_dir, exist_ok=True)
    
    output_path = os.path.join(sheets_dir, filename)
    layout_path = os.path.join(sheets_dir, layout_filename)
    
    try:
        # Usamos el generador excelente (SIN TOCAR SU CÓDIGO)
        generator = AnswerSheetGenerator(output_path, layout_path, exam_id)
        generator.generate(num_questions=60, options=5)
        
        # Pequeña verificación de que el archivo existe
        if not os.path.exists(output_path):
            raise Exception("Error físico al escribir el PDF")
            
        return {
            "message": "PDF generado con éxito",
            "pdf_url": f"/api/generator/download/{exam_id}?v={int(time.time())}"
        }
    except Exception as e:
        print(f"Error en generación: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del motor de PDF")

@router.get("/download/{exam_id}")
async def download_pdf(exam_id: int):
    base_dir = os.getcwd()
    filename = f"ficha_examen_{exam_id}.pdf"
    output_path = os.path.join(base_dir, "data", "sheets", filename)
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
    return FileResponse(
        output_path, 
        media_type='application/pdf',
        filename=filename,
        content_disposition_type='inline'
    )
