from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_db
from backend.models.exam import Exam, AnswerKey

router = APIRouter()

class AnswerKeySchema(BaseModel):
    question_number: int
    correct_answer: str
    points: float = 1.0

class ExamCreate(BaseModel):
    name: str
    subject: str

class ExamResponse(BaseModel):
    id: int
    name: str
    subject: str
    num_questions: int
    options_per_question: int
    date: datetime
    class Config:
        from_attributes = True

@router.post("/", response_model=ExamResponse)
def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    # FORZAMOS 60 preguntas y 5 opciones (A-E)
    db_exam = Exam(
        name=exam.name,
        subject=exam.subject,
        num_questions=60,
        options_per_question=5,
        scoring_formula="simple"
    )
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

@router.get("/", response_model=List[ExamResponse])
def get_exams(db: Session = Depends(get_db)):
    return db.query(Exam).all()

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    return exam

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    db.delete(exam)
    db.commit()
    return {"message": "Examen eliminado correctamente"}

@router.post("/{exam_id}/answers")
def set_answers(exam_id: int, answers: List[AnswerKeySchema], db: Session = Depends(get_db)):
    db.query(AnswerKey).filter(AnswerKey.exam_id == exam_id).delete()
    for ans in answers:
        db_ans = AnswerKey(exam_id=exam_id, **ans.model_dump())
        db.add(db_ans)
    db.commit()
    return {"message": "Clave de respuestas actualizada"}

@router.get("/{exam_id}/answers", response_model=List[AnswerKeySchema])
def get_answers(exam_id: int, db: Session = Depends(get_db)):
    return db.query(AnswerKey).filter(AnswerKey.exam_id == exam_id).all()
