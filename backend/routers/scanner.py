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
        raise HTTPException(status_code=400, detail="Primero genera la ficha PDF")

    pipeline = OMRPipeline(layout_path)
    ocr = OCRReader()
    processed_results = []
    
    for file in files:
        file_id = str(uuid.uuid4())
        file_ext = file.filename.split(".")[-1]
        file_path = os.path.join("data", "scans", f"{file_id}.{file_ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            # 1. Procesar OMR
            omr_res = pipeline.process_image(file_path)
            
            if "error" in omr_res:
                processed_results.append({"filename": file.filename, "status": "error", "message": omr_res["error"]})
                continue

            # 2. Procesar OCR de Nombres si están disponibles
            full_name = ""
            if "name_rois" in omr_res:
                ap_p = ocr.read_name(omr_res["name_rois"].get("APELLIDO PATERNO"))
                ap_m = ocr.read_name(omr_res["name_rois"].get("APELLIDO MATERNO"))
                noms = ocr.read_name(omr_res["name_rois"].get("NOMBRES"))
                full_name = f"{ap_p} {ap_m} {noms}".strip()
                # Eliminar ROIs del diccionario (no son serializables a JSON)
                del omr_res["name_rois"]

            # Guardar en base de datos
            new_scan = Scan(
                exam_id=exam_id,
                image_path=file_path,
                raw_result_json=omr_res
            )
            db.add(new_scan)
            db.commit()
            db.refresh(new_scan)
            
            processed_results.append({
                "scan_id": new_scan.id,
                "filename": file.filename,
                "dni": omr_res.get("dni", ""),
                "ocr_name": full_name,
                "status": "success"
            })
        except Exception as e:
            print(f"Error procesando {file.filename}: {str(e)}")
            processed_results.append({"filename": file.filename, "status": "error", "message": "Fallo crítico en el motor"})
        
    return {"processed": processed_results}

@router.get("/view/{scan_id}")
async def view_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan or not os.path.exists(scan.image_path):
        raise HTTPException(status_code=404)
    return FileResponse(scan.image_path)

@router.post("/confirm/{scan_id}")
async def confirm_scan(scan_id: int, data: dict, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan: raise HTTPException(status_code=404)
    
    dni, student_name = data.get("dni"), data.get("student_name")
    
    student = db.query(Student).filter(Student.dni == dni).first()
    if not student:
        student = Student(dni=dni, name=student_name)
        db.add(student)
        db.commit()
        db.refresh(student)
    
    answer_key_list = db.query(AnswerKey).filter(AnswerKey.exam_id == scan.exam_id).all()
    key_dict = {str(ak.question_number): {"ans": ak.correct_answer, "pts": ak.points} for ak in answer_key_list}
    
    exam = db.query(Exam).filter(Exam.id == scan.exam_id).first()
    grade = Grader.calculate_score(scan.raw_result_json["answers"], key_dict, formula=exam.scoring_formula)
    
    new_result = Result(
        scan_id=scan.id, student_id=student.id, exam_id=scan.exam_id,
        score=grade["score"], correct=grade["correct"], wrong=grade["wrong"], blank=grade["blank"],
        answers_json=scan.raw_result_json["answers"], flags_json={}
    )
    
    db.add(new_result)
    scan.student_id = student.id
    db.commit()
    return {"status": "success"}

