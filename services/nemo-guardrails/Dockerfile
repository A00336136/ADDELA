FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir nemoguardrails fastapi uvicorn
COPY nemo_config ./nemo_config
COPY app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
