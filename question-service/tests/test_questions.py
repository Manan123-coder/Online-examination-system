def make_exam(client):
    return client.post("/exams", json={"title": "Python Basics", "duration": 30}).json()


def test_create_exam(client):
    r = client.post("/exams", json={"title": "Python Basics", "duration": 30})
    assert r.status_code == 201
    assert r.json()["title"] == "Python Basics"
    assert len(client.get("/exams").json()) == 1


def test_create_question(client):
    exam = make_exam(client)
    body = {"exam_id": exam["id"], "question": "What is Python?", "option_a": "Language",
            "option_b": "Database", "option_c": "OS", "option_d": "Browser", "correct_answer": "A"}
    assert client.post("/questions", json=body).status_code == 201
    questions = client.get(f"/questions/{exam['id']}").json()
    assert len(questions) == 1
    assert "correct_answer" not in questions[0]  # students must not see answers


def test_invalid_correct_answer_rejected(client):
    exam = make_exam(client)
    body = {"exam_id": exam["id"], "question": "Q?", "option_a": "a", "option_b": "b",
            "option_c": "c", "option_d": "d", "correct_answer": "Z"}
    assert client.post("/questions", json=body).status_code == 422  # input validation
