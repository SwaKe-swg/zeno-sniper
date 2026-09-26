# zeno-sniper Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ENTRYPOINT esplicito: garantisce che parta main.py anche se Railway
# sovrascrive il CMD o usa un startCommand di default (es. "python app.py").
ENTRYPOINT ["python", "main.py"]
