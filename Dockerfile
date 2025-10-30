# Używamy lekkiego obrazu z Pythonem
FROM python:3.10-slim

# Ustawiamy katalog roboczy w kontenerze
WORKDIR /app

# Kopiujemy pliki do kontenera
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Aplikacja wystawi API na porcie 5000
EXPOSE 5000

# Komenda startowa kontenera
CMD ["python", "app.py"]

