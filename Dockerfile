FROM python:3.11

# ChromaDB packages
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --no-deps -r requirements.txt

COPY . .

CMD ["python", "main.py"]
