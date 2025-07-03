FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Ensure FAISS index folder exists
RUN mkdir -p /app/knowledge_base

# Make sure Python can find app modules
ENV PYTHONPATH=/app

# Run both Flask and Streamlit from main.py
ENTRYPOINT ["python", "main.py"]