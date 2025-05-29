FROM python:3.12-slim

WORKDIR app/

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
COPY .dockerignore .

RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

RUN chmod +x ./src/prestart.sh

ENTRYPOINT ["./src/prestart.sh"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]