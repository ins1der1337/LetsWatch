FROM python:3.12-slim

WORKDIR app/

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
COPY .dockerignore .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

CMD ["python", "./src/run.py"]