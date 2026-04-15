FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY ai_core /app/ai_core

WORKDIR /app/backend
RUN sed -i 's/\r$//' /app/backend/start.sh && chmod +x /app/backend/start.sh
EXPOSE 1111

CMD ["sh", "./start.sh"]
