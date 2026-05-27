FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD python manage.py check --deploy 2>&1 || true && \
    python -c "import django; django.setup(); print('[STARTUP OK] Django cargó sin errores')" && \
    gunicorn backend_config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    --timeout 120