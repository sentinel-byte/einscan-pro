from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String, unique=True, index=True)
    name = Column(String)
    classroom = Column(String, nullable=True)
    program = Column(String, nullable=True)

    results = relationship("Result", back_populates="student")
