import numpy as np
from typing import List, Dict

class Grader:
    @staticmethod
    def calculate_score(student_answers: Dict, answer_key: Dict, formula="simple"):
        """
        Calcula el puntaje de un estudiante.
        student_answers: { "1": "A", "2": "B", ... }
        answer_key: { "1": {"ans": "A", "pts": 1.0}, ... }
        """
        correct = 0
        wrong = 0
        blank = 0
        total_score = 0.0
        
        details = {}
        
        for q_num, key_info in answer_key.items():
            correct_ans = key_info["ans"]
            pts = key_info["pts"]
            student_ans = student_answers.get(str(q_num))
            
            if not student_ans:
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
        """
        Calcula estadísticas generales de un examen.
        results: Lista de diccionarios con 'score' y 'answers_json'
        """
        if not results:
            return {}
            
        scores = [r["score"] for r in results]
        
        stats = {
            "mean": float(np.mean(scores)),
            "median": float(np.median(scores)),
            "std_dev": float(np.std(scores)),
            "min": float(np.min(scores)),
            "max": float(np.max(scores)),
            "count": len(results),
            "distribution": np.histogram(scores, bins=10, range=(0, 100))[0].tolist()
        }
        
        return stats

    @staticmethod
    def item_analysis(results: List[Dict], answer_key: Dict):
        """
        Analiza dificultad y discriminación por pregunta.
        """
        if not results: return {}
        
        analysis = {}
        num_students = len(results)
        
        # Ordenar estudiantes por puntaje para discriminación
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
        top_27 = sorted_results[:max(1, int(num_students * 0.27))]
        bottom_27 = sorted_results[-max(1, int(num_students * 0.27)):]
        
        for q_num in answer_key.keys():
            correct_ans = answer_key[q_num]["ans"]
            
            # Dificultad: % de aciertos
            hits = sum(1 for r in results if r["answers_json"].get(str(q_num)) == correct_ans)
            difficulty = hits / num_students
            
            # Discriminación: (aciertos_top - aciertos_bottom) / N_grupo
            top_hits = sum(1 for r in top_27 if r["answers_json"].get(str(q_num)) == correct_ans)
            bot_hits = sum(1 for r in bottom_27 if r["answers_json"].get(str(q_num)) == correct_ans)
            discrimination = (top_hits - bot_hits) / len(top_27)
            
            analysis[q_num] = {
                "difficulty_index": round(difficulty, 2),
                "discrimination_index": round(discrimination, 2)
            }
            
        return analysis
