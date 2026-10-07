NEW = {"name": "Asha", "email": "asha@example.com", "password": "secret123"}


def test_register_student(client):
    r = client.post("/students/register", json=NEW)
    assert r.status_code == 201
    assert r.json()["email"] == "asha@example.com"
    assert "password" not in r.json()  # password must never be returned


def test_login_student(client):
    client.post("/students/register", json=NEW)
    ok = client.post("/students/login", json={"email": NEW["email"], "password": NEW["password"]})
    assert ok.status_code == 200 and "access_token" in ok.json()
    bad = client.post("/students/login", json={"email": NEW["email"], "password": "wrong-pass"})
    assert bad.status_code == 401


def test_protected_endpoint_needs_token(client):
    student = client.post("/students/register", json=NEW).json()
    assert client.get(f"/students/{student['id']}").status_code in (401, 403)  # no token
    token = client.post("/students/login", json={"email": NEW["email"], "password": NEW["password"]}).json()["access_token"]
    r = client.get(f"/students/{student['id']}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200 and r.json()["name"] == "Asha"
