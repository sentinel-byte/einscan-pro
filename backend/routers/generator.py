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
    
    # Rutas absolutas para Render
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filename = f"ficha_examen_{exam_id}.pdf"
    layout_filename = f"{exam_id}_layout.json"
    
    sheets_dir = os.path.join(base_dir, "data", "sheets")
    os.makedirs(sheets_dir, exist_ok=True)
    
    output_path = os.path.join(sheets_dir, filename)
    layout_path = os.path.join(sheets_dir, layout_filename)
    
    print(f"DEBUG: Generando PDF en {output_path}...")
    
    try:
        generator = AnswerSheetGenerator(output_path, layout_path, exam_id)
        generator.generate(num_questions=60, options=5)
        
        # Validación de supervivencia del archivo
        time.sleep(0.5) # Pequeña espera para asegurar escritura en disco
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            print(f"ERROR: El archivo PDF no se creó correctamente en {output_path}")
            raise Exception("El archivo generado está vacío o no existe.")
            
        print(f"DEBUG: PDF generado con éxito. Tamaño: {os.path.getsize(output_path)} bytes")
        
        return {
            "message": "PDF generado con éxito",
            "pdf_url": f"/api/generator/download/{exam_id}?t={int(time.time())}" # Cache busting
        }
    except Exception as e:
        print(f"CRITICAL ERROR generando PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno al crear el PDF: {str(e)}")

@router.get("/download/{exam_id}")
async def download_pdf(exam_id: int):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filename = f"ficha_examen_{exam_id}.pdf"
    output_path = os.path.join(base_dir, "data", "sheets", filename)
    
    if not os.path.exists(output_path):
        print(f"ERROR: Intento de descarga de PDF inexistente: {output_path}")
        raise HTTPException(status_code=404, detail="El archivo PDF no se encuentra en el servidor.")
        
    return FileResponse(
        output_path, 
        media_type='application/pdf',
        filename=filename,
        content_disposition_type='inline'
    )

