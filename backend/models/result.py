from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    image_path = Column(String)
    raw_result_json = Column(JSON)
    processed_at = Column(DateTime, default=datetime.utcnow)

    result = relationship("Result", back_populates="scan", uselist=False)

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    
    score = Column(Float)
    correct = Column(Integer)
    wrong = Column(Integer)
    blank = Column(Integer)
    
    answers_json = Column(JSON) # El detalle de cada respuesta
    flags_json = Column(JSON)   # Marcas de advertencia (doble marca, etc)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="result")
    student = relationship("Student", back_populates="results")
    exam = relationship("Exam", back_populates="results")
