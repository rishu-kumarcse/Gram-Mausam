FROM python:3.12-slim

# Avoid buffering and bytecode
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOST=0.0.0.0 \
    HOME=/home/user

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create Hugging Face default non-root user (UID 1000)
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# Pre-install CPU-only PyTorch (reduces image from 2.5GB+ to <800MB)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install project Python requirements
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy application code and assets
COPY --chown=user:user . .

# Switch to non-root user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Hugging Face default container port
EXPOSE 7860

# Launch server
CMD ["python", "run_server.py"]
