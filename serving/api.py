import os
import sys
import logging
import hashlib
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import uvicorn
import requests
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter

# --- 1. CONFIGURATION & LOGGING ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mlops_api")

# Paths (Τα αφήνουμε, αλλά θα τα διαχειριστούμε προσεκτικά)
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:////app/mlflow.db")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
TRAFFIC_RATIO = float(os.getenv("STAGING_TRAFFIC_RATIO", 0.1))

# --- 2. MOCK MODEL FOR DEMO SAFETY ---
class DummyModel:
    def predict(self, df):
        # Αν το ποσό είναι πάνω από 4000, επέστρεψε 1 (Fraud)
        amount = df['amount'].iloc[0]
        return [1] if amount > 4000 else [0]

# --- 3. LOAD MODELS (SAFE VERSION) ---
model_prod = DummyModel()
model_staging = DummyModel()
is_using_dummy = True

try:
    import mlflow.pyfunc
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Δοκιμάζουμε να φορτώσουμε μόνο αν υπάρχουν τα paths
    prod_path = os.getenv("PROD_MODEL_URI", "/app/mlruns/0/models/m-5f7b1f8d4fc3479484b4f1ede3a002ab/artifacts")
    if os.path.exists(prod_path):
        model_prod = mlflow.pyfunc.load_model(prod_path)
        model_staging = model_prod # Για το demo ας είναι το ίδιο αν δεν υπάρχει staging
        is_using_dummy = False
        logger.info("✅ MLflow model loaded successfully!")
    else:
        logger.warning(f"⚠️ Model path {prod_path} not found. Using DummyModel.")
except Exception as e:
    logger.warning(f"⚠️ Could not initialize MLflow: {e}. Falling back to DummyModel.")

# --- 4. API SETUP ---
app = FastAPI(title="Fraud Detection API - Stable Version")
Instrumentator().instrument(app).expose(app)

PREDICTIONS_TOTAL = Counter('predictions_total', 'Total predictions', ['variant', 'label'])

class TransactionRequest(BaseModel):
    user_id: str
    amount: float
    merchant_category_enc: int
    timestamp: str

# --- 5. HELPERS ---
def get_model_variant(user_id: str) -> str:
    hash_val = hashlib.md5(user_id.encode()).hexdigest()
    index = int(hash_val, 16) % 100
    return "staging" if index < (TRAFFIC_RATIO * 100) else "production"

def get_phi3_explanation(amount, label):
    # Απλοποιημένο για να μην κολλάει αν το Ollama είναι αργό
    try:
        prompt = f"Explain briefly why a transaction of {amount} EUR is flagged as {label}."
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": "phi3:mini", "prompt": prompt, "stream": False},
            timeout=2 # Πολύ μικρό timeout για να μην κρεμάει το API
        )
        return resp.json().get("response", "High risk transaction detected.")
    except:
        return "Transaction exceeds safety thresholds for this user profile."

# --- 6. ENDPOINTS ---
@app.post("/predict")
async def predict(request: TransactionRequest):
    try:
        dt = pd.to_datetime(request.timestamp)
        feature_vector = {
            "amount": request.amount,
            "hour": dt.hour,
            "day_of_week": dt.dayofweek,
            "merchant_category_enc": request.merchant_category_enc
        }
        
        variant = get_model_variant(request.user_id)
        selected_model = model_staging if variant == "staging" else model_prod
        
        input_df = pd.DataFrame([feature_vector])
        prediction = selected_model.predict(input_df)
        
        is_fraud = int(prediction[0])
        label = "FRAUD" if is_fraud == 1 else "NORMAL"
        
        PREDICTIONS_TOTAL.labels(variant=variant, label=label).inc()
        
        explanation = "Normal pattern"
        if is_fraud:
            explanation = get_phi3_explanation(request.amount, label)

        return {
            "variant_used": variant,
            "is_fraud": is_fraud,
            "label": label,
            "llm_explanation": explanation,
            "mode": "Demo (Rules)" if is_using_dummy else "MLflow (AI)"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "dummy_mode": is_using_dummy}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)