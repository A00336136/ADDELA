FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir presidio-analyzer fastapi uvicorn
RUN python -m spacy download en_core_web_lg
COPY app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
