FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y ffmpeg pandoc poppler-utils && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip

COPY . .
CMD ["python", "main.py"]
