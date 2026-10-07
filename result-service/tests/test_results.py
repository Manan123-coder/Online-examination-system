from app.scoring import calculate_score


def test_calculate_result():
    correct = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "A"}
    answers = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "B"}  # 4 right, 1 wrong
    assert calculate_score(correct, answers) == (4, 5, 80.0)


def test_submit_exam(client, auth_header, monkeypatch):
    # Pretend the Question Service answered, so this test needs no other service running.
    monkeypatch.setattr("app.main.fetch_correct_answers", lambda exam_id: {"1": "A", "2": "B"})
    r = client.post("/results/submit", json={"exam_id": 1, "answers": {"1": "A", "2": "C"}},
                    headers=auth_header)
    assert r.status_code == 201
    assert r.json()["score"] == 1 and r.json()["percentage"] == 50.0
    assert len(client.get("/results", headers=auth_header).json()) == 1


def test_submit_requires_token(client):
    r = client.post("/results/submit", json={"exam_id": 1, "answers": {}})
    assert r.status_code in (401, 403) 
