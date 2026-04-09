🛡️ Real-Time Fraud Detection MLOps Platform
Μια ολοκληρωμένη πλατφόρμα ανίχνευσης απάτης (Fraud Detection) που καλύπτει όλο τον κύκλο ζωής ενός μοντέλου ML: από το feature engineering και το tracking, μέχρι το production deployment και το Explainable AI (XAI).

🚀 Key Features
Production-Ready API: Αναπτυγμένο με FastAPI και πλήρως containerized μέσω Docker.

Hybrid Inference Engine: Σύστημα με Failover Mechanism. Αν το MLflow artifact store δεν είναι διαθέσιμο, το API γυρνάει αυτόματα σε logic-based inference για μηδενικό downtime.

Feature Store Integration: Σύνδεση με Redis για real-time enrichment των συναλλαγών.

MLOps Tracking: Χρήση MLflow για την παρακολούθηση πειραμάτων, μοντέλων και εκδόσεων (versioning).

A/B Testing: Ενσωματωμένο traffic splitting (Production vs Staging) βασισμένο σε user-id hashing.

Explainable AI (XAI): Ενοποίηση με LLM (Phi-3 via Ollama) για την παροχή φυσικής γλώσσας ως εξήγηση σε κάθε "Fraud" alert.

Observability: Έκθεση metrics σε μορφή Prometheus για monitoring.

🛠️ Architecture Overview
Data Layer: Feature engineering pipelines σε Python/Pandas.

Storage Layer: Redis (Online Feature Store) & SQLite (MLflow Metadata).

Model Layer: MLflow για Model Registry.

Serving Layer: FastAPI Docker Container.

Explanation Layer: LLM Agent (Ollama) για interpretation των προβλέψεων.

📦 Installation & Setup
1. Clone the repository

git clone https://github.com/your-username/fraud-detection-mlops.git
cd fraud-detection-mlops

2. Build and Run with Docker
Παρά το legacy docker-compose environment, η εφαρμογή μπορεί να σηκωθεί σταθερά με:

# Build the image
sudo docker build -t fraud-api -f Dockerfile .

# Run the container
sudo docker run -d \
  --name fraud-api-service \
  -p 8000:8000 \
  -e PYTHONPATH=/app \
  fraud-api

  📡 API Usage
Health Check

curl http://localhost:8000/health

Get Prediction

curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_1234",
       "amount": 5500.0,
       "merchant_category_enc": 1,
       "timestamp": "2026-04-09T10:00:00"
     }'

     📈 Monitoring & Metrics
Το API εκθέτει metrics στη διεύθυνση http://localhost:8000/metrics, έτοιμα για κατανάλωση από Prometheus και απεικόνιση σε Grafana.

🛡️ Resilience & Engineering Excellence
Το project ακολουθεί την αρχή του Graceful Degradation. Σε περίπτωση αστοχίας του MLflow registry, το σύστημα ενεργοποιεί ένα DummyModel βασισμένο σε επιχειρηματικούς κανόνες, διασφαλίζοντας ότι το business logic παραμένει ενεργό 24/7.

Developed by Dimitris | MLOps Engineer Candidate 🚀