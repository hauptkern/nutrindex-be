FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

FROM python:3.11-slim as final

RUN adduser --disabled-password --gecos "" --no-create-home nutrindex

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .
RUN chown -R nutrindex:nutrindex /app

USER nutrindex

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Uncomment the following line if using Gunicorn
# CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]