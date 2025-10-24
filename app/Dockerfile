FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn pymongo redis python-dotenv

EXPOSE 8000

# Importante: ruta completa al main
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
