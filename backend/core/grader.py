import numpy as np
from typing import List, Dict

class Grader:
    @staticmethod
    def calculate_score(student_answers: Dict, answer_key: Dict, formula="simple"):
        """
        Calcula el puntaje de un estudiante para 60 preguntas fijas.
        """
        correct = 0
        wrong = 0
        blank = 0
        total_score = 0.0
        details = {}
        
        # Iterar exactamente sobre 60 preguntas
        for q_num in range(1, 61):
            key_info = answer_key.get(str(q_num))
            student_ans = student_answers.get(str(q_num))
            
            if not key_info:
                # Si el docente no puso clave para esta pregunta, no se cuenta
                continue
                
            correct_ans = key_info["ans"]
            pts = key_info.get("pts", 1.0)
            
            if not student_ans or student_ans == "":
                blank += 1
                details[q_num] = "blank"
            elif student_ans == correct_ans:
                correct += 1
                total_score += pts
                details[q_num] = "correct"
            else:
                wrong += 1
                if formula == "penalty":
                    total_score -= (pts * 0.25)
                details[q_num] = "wrong"
                
        return {
            "score": max(0, total_score),
            "correct": correct,
            "wrong": wrong,
            "blank": blank,
            "details": details
        }

    @staticmethod
    def calculate_statistics(results: List[Dict]):
        if not results:
            return {"mean": 0, "median": 0, "std_dev": 0, "min": 0, "max": 0, "count": 0, "distribution": []}
            
        scores = [r["score"] for r in results]
        return {
            "mean": float(np.mean(scores)),
            "median": float(np.median(scores)),
            "std_dev": float(np.std(scores)),
            "min": float(np.min(scores)),
            "max": float(np.max(scores)),
            "count": len(results),
            "distribution": np.histogram(scores, bins=10, range=(0, 60))[0].tolist()
        }

    @staticmethod
    def item_analysis(results: List[Dict], answer_key: Dict):
        if not results: return {}
        analysis = {}
        num_students = len(results)
        
        for q_num in range(1, 61):
            key_info = answer_key.get(str(q_num))
            if not key_info: continue
            
            correct_ans = key_info["ans"]
            hits = sum(1 for r in results if r["answers_json"].get(str(q_num)) == correct_ans)
            difficulty = hits / num_students
            
            analysis[q_num] = {
                "difficulty_index": round(difficulty, 2),
                "discrimination_index": 0 # Simplificado
            }
        return analysis

