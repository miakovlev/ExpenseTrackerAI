FROM python:3.12-slim

RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

COPY . /app

ENV PYTHONPATH=/app

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN chown -R appuser:appuser /app

USER appuser

CMD ["python", "bot/app.py"]