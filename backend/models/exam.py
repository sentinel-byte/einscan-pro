from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    num_questions = Column(Integer)
    options_per_question = Column(Integer, default=5) # A-E
    scoring_formula = Column(String, default="simple") # simple, weighted, penalty
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("AnswerKey", back_populates="exam", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="exam")

class AnswerKey(Base):
    __tablename__ = "answer_keys"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    question_number = Column(Integer)
    correct_answer = Column(String)
    points = Column(Float, default=1.0)

    exam = relationship("Exam", back_populates="questions")
