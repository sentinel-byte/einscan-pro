import os
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import shutil

from backend.database import get_db
from backend.models.exam import Exam, AnswerKey
from backend.models.student import Student
from backend.models.result import Scan, Result
from backend.core.omr_pipeline import OMRPipeline
from backend.core.ocr_reader import OCRReader
from backend.core.grader import Grader

router = APIRouter()

@router.post("/upload/{exam_id}")
async def upload_scans(
    exam_id: int, 
    files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
        
    layout_path = os.path.join("data", "sheets", f"{exam_id}_layout.json")
    if not os.path.exists(layout_path):
        raise HTTPException(status_code=400, detail="Primero genera la ficha PDF para este examen")

    pipeline = OMRPipeline(layout_path)
    processed_results = []
    
    for file in files:
        file_id = str(uuid.uuid4())
        file_ext = file.filename.split(".")[-1]
        file_path = os.path.join("data", "scans", f"{file_id}.{file_ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Ejecutar OMR real
        try:
            raw_result = pipeline.process_image(file_path)
            
            if not raw_result or "error" in raw_result:
                processed_results.append({
                    "filename": file.filename, 
                    "status": "error", 
                    "message": raw_result.get("error", "Error desconocido") if raw_result else "No se pudo procesar"
                })
                continue

            # Guardar en base de datos
            new_scan = Scan(
                exam_id=exam_id,
                image_path=file_path,
                raw_result_json=raw_result
            )
            db.add(new_scan)
            db.commit()
            db.refresh(new_scan)
            
            processed_results.append({
                "scan_id": new_scan.id,
                "filename": file.filename,
                "dni": raw_result.get("dni", ""),
                "exam_type": raw_result.get("exam_type", "A"),
                "status": "success"
            })
        except Exception as e:
            processed_results.append({"filename": file.filename, "status": "error", "message": str(e)})
        
    return {"processed": processed_results}

@router.get("/view/{scan_id}")
async def view_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan or not os.path.exists(scan.image_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(scan.image_path)

@router.post("/confirm/{scan_id}")
async def confirm_scan(
    scan_id: int, 
    data: dict, # Recibir DNI y Nombre
    db: Session = Depends(get_db)
):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado")
        
    dni = data.get("dni")
    student_name = data.get("student_name", f"Estudiante {dni}")
    
    # 1. Buscar o registrar estudiante
    student = db.query(Student).filter(Student.dni == dni).first()
    if not student:
        student = Student(dni=dni, name=student_name)
        db.add(student)
        db.commit()
        db.refresh(student)
    
    # 2. Obtener clave de respuestas
    answer_key_list = db.query(AnswerKey).filter(AnswerKey.exam_id == scan.exam_id).all()
    key_dict = {str(ak.question_number): {"ans": ak.correct_answer, "pts": ak.points} for ak in answer_key_list}
    
    # 3. Calificar
    exam = db.query(Exam).filter(Exam.id == scan.exam_id).first()
    grade = Grader.calculate_score(scan.raw_result_json["answers"], key_dict, formula=exam.scoring_formula)
    
    # 4. Guardar Resultado final
    new_result = Result(
        scan_id=scan.id,
        student_id=student.id,
        exam_id=scan.exam_id,
        score=grade["score"],
        correct=grade["correct"],
        wrong=grade["wrong"],
        blank=grade["blank"],
        answers_json=scan.raw_result_json["answers"],
        flags_json={"ambiguous_count": scan.raw_result_json.get("ambiguous_count", 0)}
    )
    
    db.add(new_result)
    scan.student_id = student.id
    db.commit()
    
    return {"status": "success", "result_id": new_result.id}
