FROM python:3.13-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/run.py .
COPY infrastructure/database/001_initial_schema.sql ./schema.sql

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]