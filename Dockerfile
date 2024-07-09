FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY app/ entrypoint.sh /app/

RUN chmod +x entrypoint.sh

WORKDIR /

ENTRYPOINT ["sh", "/app/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

