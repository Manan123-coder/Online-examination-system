def calculate_score(correct_answers: dict, student_answers: dict):
    """correct_answers = {"1": "A", "2": "C"}   student_answers = {"1": "A", "2": "B"}
    Returns (score, total_questions, percentage)."""
    total = len(correct_answers)
    score = sum(1 for qid, right in correct_answers.items() if student_answers.get(qid) == right)
    percentage = round(score / total * 100, 2) if total else 0.0
    return score, total, percentage
