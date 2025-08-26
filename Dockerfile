FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml* requirements.txt* ./

RUN if [ -f "pyproject.toml" ]; then \
      pip install --no-cache-dir -U pip && pip install --no-cache-dir . ; \
    elif [ -f "requirements.txt" ]; then \
      pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt ; \
    fi

COPY . .

EXPOSE 5001 8765
