FROM python:3.11-slim

WORKDIR /minio_app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY minio_app/ .

WORKDIR /

CMD ["uvicorn", "minio_app.minio:app", "--host", "0.0.0.0", "--port", "8001"]

