from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.exam import Exam, AnswerKey
from backend.models.result import Result
from backend.models.student import Student
from backend.core.grader import Grader

router = APIRouter()

@router.get("/{exam_id}")
async def get_results(exam_id: int, db: Session = Depends(get_db)):
    results = db.query(Result).filter(Result.exam_id == exam_id).all()
    response = []
    for r in results:
        student = db.query(Student).filter(Student.id == r.student_id).first()
        response.append({
            "id": r.id,
            "student_name": student.name if student else "Desconocido",
            "dni": student.dni if student else "00000000",
            "score": r.score,
            "correct": r.correct,
            "wrong": r.wrong,
            "blank": r.blank,
            "processed_at": r.created_at
        })
    return response

@router.get("/{exam_id}/stats")
async def get_exam_stats(exam_id: int, db: Session = Depends(get_db)):
    results = db.query(Result).filter(Result.exam_id == exam_id).all()
    if not results:
        return {
            "summary": {"mean": 0, "max": 0, "min": 0, "count": 0, "std_dev": 0},
            "item_analysis": {}
        }
    results_list = [{"score": r.score, "answers_json": r.answers_json} for r in results]
    stats = Grader.calculate_statistics(results_list)
    answer_keys = db.query(AnswerKey).filter(AnswerKey.exam_id == exam_id).all()
    key_dict = {str(ak.question_number): {"ans": ak.correct_answer} for ak in answer_keys}
    item_analysis = Grader.item_analysis(results_list, key_dict)
    return {
        "summary": stats,
        "item_analysis": item_analysis
    }
