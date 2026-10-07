# A Dockerfile is the recipe used to build an IMAGE.
FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# The version is stored inside the image and shown on /health
ARG APP_VERSION=1.0
ENV APP_VERSION=$APP_VERSION
# Run as a normal user (not root) - basic security. /data holds the SQLite file.
RUN useradd -m appuser && mkdir /data && chown appuser /data
USER appuser
ENV DATABASE_URL=sqlite:////data/question.db
EXPOSE 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
