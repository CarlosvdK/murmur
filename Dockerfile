FROM python:3.11-slim

WORKDIR /app

# Install CPU-only PyTorch first (much smaller than default)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY research/ ./research/
COPY config/ ./config/

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
