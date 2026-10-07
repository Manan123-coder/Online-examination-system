# SERVICE-TO-SERVICE REST COMMUNICATION happens here:
# Result Service  --HTTP GET-->  Question Service  (to fetch the correct answers)
import os

import httpx
from fastapi import HTTPException

# In Docker/Kubernetes the hostname "question-service" is the service name (DNS).
QUESTION_SERVICE_URL = os.getenv("QUESTION_SERVICE_URL", "http://localhost:8002")


def fetch_correct_answers(exam_id: int) -> dict:
    try:
        response = httpx.get(f"{QUESTION_SERVICE_URL}/internal/answers/{exam_id}", timeout=5)
        response.raise_for_status()
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Question Service is not reachable")
    return response.json()
