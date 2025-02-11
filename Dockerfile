FROM python:3.12-slim

WORKDIR /app

COPY . /app

ENV PYTHONPATH=/app

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "bot/app.py"]