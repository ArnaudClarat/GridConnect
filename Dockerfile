FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances système si nécessaire (ex: build-deps pour psycopg2/TimescaleDB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source et de la configuration
COPY . .

# Commande pour tourner en boucle toutes les heures (ou géré par l'OS/cron, voir option Docker Compose)
CMD ["python", "scripts/daemon.py"]