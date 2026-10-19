# Multi-Stage, Production-Grade Dockerfile for MSME Compliance & Funding Copilot
# Team TEJAS066 • Temenos CSR & SASTRA University Hackathon Finals 2026
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8501

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy complete project codebase
COPY . .

# Expose Streamlit default web port
EXPOSE 8501

# Healthcheck probe to verify Streamlit application is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Master Orchestrator: runs full verification then starts Streamlit UI
CMD ["sh", "-c", "python run_pipeline.py && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
