# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Avoid Python writing pyc files and enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
# Copy backend code
COPY . .

# Expose FastAPI port
EXPOSE 8000


# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
