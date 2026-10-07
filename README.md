# Online Examination Platform (MScIT project)

Three FastAPI microservices + React frontend, with JWT, tests, Docker, Jenkins, Kubernetes, rollback, security checks and monitoring.

```
                React (port 3000)  -- nginx forwards /api/... --
                       |
      +----------------+----------------+
      v                v                v
 Student Service  Question Service  Result Service      (8001 / 8002 / 8003)
   student.db       question.db       result.db
                         ^                |
                         +-- REST call ---+   (Result asks Question for correct answers)
```

| Folder / file | Purpose |
|---|---|
| `student-service/` | register, login (JWT), student CRUD |
| `question-service/` | exams + MCQ questions CRUD (a sample "Python Basics" exam is added on first start) |
| `result-service/` | marks answers, saves score/percentage, result history |
| `frontend/` | React (Vite) website |
| `k8s/` | Kubernetes Deployment + Service files |
| `monitoring/` | Prometheus + Grafana config |
| `Jenkinsfile`, `docker-compose.yml` | CI/CD and container setup |

## Option A: Run with Docker (easiest)
Requires Docker Desktop.
```bash
cp .env.example .env            # Windows: copy .env.example .env   (then edit SECRET_KEY)
docker compose up --build
```
* Website: http://localhost:3000 (register, login, take the exam)
* Health: http://localhost:8001/health, 8002, 8003
* Prometheus: http://localhost:9090  | Grafana: http://localhost:3001 (admin / admin) -> dashboard "Online Exam - Basic Monitoring"

## Option B: Run without Docker (development)
Needs Python 3.12 and Node 20. Open 4 terminals.
```bash
cd student-service  && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --port 8001 --reload
cd question-service && (same)  ... --port 8002
cd result-service   && (same)  ... --port 8003 --reload     # set QUESTION_SERVICE_URL if not localhost:8002
cd frontend && npm install && npm run dev                   # http://localhost:3000
```
(Windows: use `venv\Scripts\activate`.)

## Tests
```bash
pip install -r requirements-dev.txt
cd student-service && pip install -r requirements.txt && pytest
cd ../question-service && pip install -r requirements.txt && pytest
cd ../result-service && pip install -r requirements.txt && pytest
```
Expected: 3 tests pass in each service. Tests use a separate `test_*.db` file.

## Security checks
```bash
cd student-service
bandit -r . -x ./tests,./venv     # scans OUR code for insecure patterns
pip-audit -r requirements.txt     # checks libraries for known vulnerabilities (needs internet)
```
Security shown: bcrypt password hashing, JWT with expiry, Pydantic input validation, secret key from environment (`.env` is git-ignored), passwords never returned by the API, containers run as non-root, internal answers endpoint blocked at nginx.

## Docker image versioning
```bash
VERSION=1.0 docker compose build      # Windows PowerShell: $env:VERSION="1.0"; docker compose build
VERSION=1.1 docker compose build
docker images                         # student-service:1.0 and student-service:1.1 both exist
```
The tag (1.0, 1.1) identifies a version, so an older one can always be restored. `/health` shows the version inside the running container.

## Kubernetes (Minikube) and rollback
```bash
minikube start
eval $(minikube docker-env)           # PowerShell: minikube docker-env | Invoke-Expression
docker build -t student-service:1.0 --build-arg APP_VERSION=1.0 ./student-service
docker build -t question-service:1.0 --build-arg APP_VERSION=1.0 ./question-service
docker build -t result-service:1.0 --build-arg APP_VERSION=1.0 ./result-service
docker build -t frontend:1.0 ./frontend

kubectl create secret generic jwt-secret --from-literal=SECRET_KEY=my-long-random-secret
kubectl apply -f k8s/
kubectl get pods
kubectl get services
minikube service frontend --url       # open this URL in the browser
```
**Rollback demo**
```bash
docker build -t student-service:1.1 --build-arg APP_VERSION=1.1 ./student-service
kubectl set image deployment/student-service student-service=student-service:1.1   # upgrade (v1.1)
kubectl rollout history deployment/student-service
# simulate a bad release: this image does not exist, so the new pod fails
kubectl set image deployment/student-service student-service=student-service:9.9
kubectl get pods                      # new pod shows ErrImageNeverPull; old pod keeps running
kubectl rollout undo deployment/student-service      # ROLLBACK to the previous version
kubectl rollout status deployment/student-service
```

## Jenkins
Create a "Pipeline from SCM" job pointing to your GitHub repo. Jenkins needs Python 3, Docker and Docker Compose on the agent. Stages: Checkout -> Install Dependencies -> Security Check -> Run Tests -> Build Docker Images -> Deploy.

---
## Viva cheat-sheet
* **Microservices**: small independent services, one job each, own database, own port, deployed/rolled back separately.
* **REST**: services talk with HTTP + JSON (GET/POST/PUT/DELETE). React -> services via Axios (`frontend/src/api.js`); Result -> Question via httpx (`result-service/app/question_client.py`).
* **JWT**: after login Student Service signs a token (header.payload.signature) with SECRET_KEY. React stores it and sends `Authorization: Bearer <token>`. Result Service verifies it with the same key. Expired/fake token -> 401.
* **Password hashing**: bcrypt stores a salted hash, never the real password.
* **Correct answers hidden**: `GET /questions/{exam_id}` never includes `correct_answer`; only the internal endpoint used by Result Service does.
* **Docker**: Dockerfile = recipe, image = packaged app, container = running image, port mapping `8001:8001`, Compose = starts all containers together.
* **Image versioning**: tags like `:1.0`, `:1.1` identify versions; Jenkins uses `1.<build number>`.
* **Jenkins**: reads the Jenkinsfile and automatically runs checkout, security scan, tests, build, deploy.
* **Kubernetes**: Deployment keeps pods (containers) running; Service gives a stable name/address; readiness probe checks `/health`.
* **Rollback**: Kubernetes remembers earlier revisions; `kubectl rollout undo` returns to the previous working version.
* **Monitoring**: each service exposes `/metrics`; Prometheus collects them every 15 s; Grafana draws availability, request rate, CPU and memory.

## Known simple limits (fine for a project, not production)
SQLite files live in a Docker volume (in Kubernetes they are lost when a pod is recreated); exam creation endpoints are open (no admin role); CORS is open; Grafana uses the default password.
