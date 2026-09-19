FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV PORT=5001
EXPOSE 5001
CMD ["sh", "-c", "gunicorn -w 2 -b 0.0.0.0:$PORT app:app"]
