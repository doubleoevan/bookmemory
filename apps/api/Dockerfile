FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --upgrade pip && \
    pip install -e .

# install chromium and system dependencies required by playwright
RUN python -m playwright install --with-deps chromium

EXPOSE 8000

# run the API and bind to all interfaces
CMD ["python", "-m", "uvicorn", "bookmemory_api.main:app", "--host", "0.0.0.0", "--port", "8000"]


