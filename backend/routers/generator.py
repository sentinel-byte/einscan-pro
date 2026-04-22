from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from backend.database import get_db
from backend.models.exam import Exam
from backend.core.pdf_generator import AnswerSheetGenerator

router = APIRouter()

@router.post("/generate/{exam_id}")
async def generate_pdf(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    
    # Rutas absolutas para Render
    base_dir = os.getcwd()
    filename = f"ficha_examen_{exam_id}.pdf"
    layout_filename = f"{exam_id}_layout.json"
    
    output_path = os.path.join(base_dir, "data", "sheets", filename)
    layout_path = os.path.join(base_dir, "data", "sheets", layout_filename)
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    generator = AnswerSheetGenerator(output_path, layout_path, exam_id)
    # Siempre generamos con 60 preguntas y 5 opciones
    generator.generate(num_questions=60, options=5)
    
    return {
        "message": "PDF generado con éxito",
        "pdf_url": f"/api/generator/download/{exam_id}"
    }

@router.get("/download/{exam_id}")
async def download_pdf(exam_id: int):
    base_dir = os.getcwd()
    filename = f"ficha_examen_{exam_id}.pdf"
    output_path = os.path.join(base_dir, "data", "sheets", filename)
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="El PDF no ha sido generado todavía.")
        
    return FileResponse(
        output_path, 
        media_type='application/pdf',
        filename=filename,
        content_disposition_type='inline'
    )
