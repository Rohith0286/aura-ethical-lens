FROM python:3.9-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy everything
COPY . .

# Install all requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Set PYTHONPATH to include backend folder for imports
ENV PYTHONPATH="${PYTHONPATH}:/app/backend"

# Create a startup script to run both FastAPI and Streamlit
# Added --server.enableCORS=false and --server.enableXsrfProtection=false to fix 403 error
RUN echo '#!/bin/bash\n\
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &\n\
streamlit run frontend/app.py --server.port 7860 --server.address 0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Hugging Face uses port 7860
EXPOSE 7860

CMD ["/app/start.sh"]
