# Minimal sandbox image for CI and containerized execution
FROM python:3.11-slim

WORKDIR /app

# Install runtime deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy repository into container (CI uses this image to run smoke tests)
COPY . /app

CMD ["python", "-c", "import agent; print('sandbox ready')"]
