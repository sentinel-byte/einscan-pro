from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from backend.database import get_db
from backend.models.exam import Exam
from backend.core.pdf_generator import AnswerSheetGenerator
from backend.auth import get_current_user

router = APIRouter()

@router.post("/generate/{exam_id}")
async def generate_pdf(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    
    filename = f"ficha_examen_{exam_id}.pdf"
    layout_filename = f"{exam_id}_layout.json"
    
    output_path = os.path.join("data", "sheets", filename)
    layout_path = os.path.join("data", "sheets", layout_filename)
    
    generator = AnswerSheetGenerator(output_path, layout_path, exam_id)
    generator.generate(num_questions=exam.num_questions, options=exam.options_per_question)
    
    return {
        "message": "PDF generado con éxito",
        "pdf_url": f"/api/generator/download/{exam_id}",
        "layout_path": layout_path
    }

@router.get("/download/{exam_id}")
async def download_pdf(exam_id: int):
    filename = f"ficha_examen_{exam_id}.pdf"
    output_path = os.path.join("data", "sheets", filename)
    
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
    # Usamos Content-Disposition: inline para que se abra en el navegador
    return FileResponse(
        output_path, 
        filename=filename, 
        media_type='application/pdf',
        content_disposition_type='inline'
    )
