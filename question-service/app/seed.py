# Adds one sample exam the first time the service starts, so the UI is not empty.
from . import models

SAMPLE = [
    ("What is Python?", "Programming Language", "Database", "Operating System", "Browser", "A"),
    ("Which symbol starts a comment in Python?", "//", "#", "/*", "--", "B"),
    ("Which keyword defines a function?", "func", "define", "def", "function", "C"),
    ("What does len([1, 2, 3]) return?", "2", "3", "4", "Error", "B"),
    ("Which type is {'a': 1}?", "list", "tuple", "set", "dict", "D"),
]


def seed_sample_exam(db):
    if db.query(models.Exam).count() > 0:
        return
    exam = models.Exam(title="Python Basics", duration=10)
    db.add(exam)
    db.commit()
    for q, a, b, c, d, ans in SAMPLE:
        db.add(models.Question(exam_id=exam.id, question=q, option_a=a, option_b=b,
                               option_c=c, option_d=d, correct_answer=ans))
    db.commit()
