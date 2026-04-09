FROM python:3.12-slim

WORKDIR /app

# 1. Εγκατάσταση εργαλείων συστήματος
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Εγκατάσταση βιβλιοθηκών
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# 3. Δημιουργία απαραίτητων φακέλων (για να μην κρασάρει το COPY)
RUN mkdir -p mlruns chroma_db

# 4. Αντιγραφή κώδικα
COPY serving/ ./serving/
COPY features/ ./features/
COPY llm_agent/ ./llm_agent/

# 5. Αντιγραφή βάσεων και μοντέλων (Αν υπάρχουν τοπικά)
# Χρησιμοποιούμε COPY . . για να πάρει ό,τι βρει, αλλά είναι πιο ασφαλές έτσι:
COPY . /app/

# 6. Ρυθμίσεις Περιβάλλοντος
ENV PYTHONPATH=/app
ENV MLFLOW_TRACKING_URI=sqlite:////app/mlflow.db
ENV OLLAMA_URL=http://host.docker.internal:11434

EXPOSE 8000

CMD ["python", "serving/api.py"]