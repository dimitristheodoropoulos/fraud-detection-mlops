"""
Fraud Detection - Production Training Pipeline
Distributed Spark + XGBoost + MLflow Model Registry
"""

import os
import logging
import mlflow
import mlflow.xgboost
from mlflow.tracking import MlflowClient
import xgboost as xgb
import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, roc_auc_score, precision_score, 
    recall_score, f1_score, confusion_matrix
)

# Configuration από Environment Variables (MLOps Best Practice)
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:////app/mlflow.db")
SPARK_MASTER = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")
DATA_PATH = "/app/data/processed_transactions.parquet"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data_distributed():
    """Φόρτωση δεδομένων χρησιμοποιώντας τον Spark Cluster."""
    logger.info(f"Connecting to Spark Master: {SPARK_MASTER}")
    spark = SparkSession.builder \
        .appName("FraudProductionTraining") \
        .master(SPARK_MASTER) \
        .config("spark.executor.memory", "1g") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()

    try:
        logger.info(f"Reading Parquet from: {DATA_PATH}")
        df_spark = spark.read.parquet(DATA_PATH)
        # Μετατροπή σε Pandas για το XGBoost (σε μεγάλα δεδομένα θα χρησιμοποιούσαμε Spark ML)
        df = df_spark.toPandas()
        return df
    finally:
        spark.stop()

def prepare_features(df):
    """Feature engineering & Preprocessing."""
    # Label Encoding για το Merchant Category
    if 'merchant_category' in df.columns:
        df["merchant_category_enc"] = pd.Categorical(df["merchant_category"]).codes
    
    feature_cols = ["amount", "hour", "day_of_week", "merchant_category_enc"]
    X = df[feature_cols].fillna(0)
    y = df["is_fraud"]
    
    return X, y, feature_cols

def train_production_model():
    """Main Training & Registration Pipeline."""
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("fraud_detection_prod")

    with mlflow.start_run(run_name="XGBoost_Production_Run") as run:
        # 1. Load & Prep
        df = load_data_distributed()
        X, y, feature_cols = prepare_features(df)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # 2. Hyperparameters με scale_pos_weight για imbalanced data (Fraud)
        params = {
            "n_estimators": 150,
            "max_depth": 5,
            "learning_rate": 0.05,
            "scale_pos_weight": int(y.value_counts()[0] / y.value_counts()[1]),
            "objective": "binary:logistic",
            "random_state": 42
        }
        mlflow.log_params(params)

        # 3. Training
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train)

        # 4. Evaluation & Financial Metrics
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        cm = confusion_matrix(y_test, y_pred)
        # Υπολογισμός "Business Impact": Κόστος ανά False Positive (π.χ. $10 για customer support)
        business_metric = cm[0][1] * 10 
        
        metrics = {
            "roc_auc": roc_auc_score(y_test, y_prob),
            "f1_score": f1_score(y_test, y_pred),
            "false_positives": cm[0][1],
            "business_cost_fp": business_metric
        }
        mlflow.log_metrics(metrics)

        # 5. Model Registration (Το κλειδί για το API)
        # Καταγράφουμε το μοντέλο και του δίνουμε το όνομα 'fraud-model-prod'
        mlflow.xgboost.log_model(
            model, 
            "model", 
            registered_model_name="fraud-detection-model"
        )
        
        logger.info(f"✅ Run Complete. AUC: {metrics['roc_auc']:.4f} | Cost FP: ${business_metric}")
        return run.info.run_id

if __name__ == "__main__":
    run_id = train_production_model()
    print(f"\n🚀 Pipeline Finished!")
    print(f"Model registered in MLflow Registry. Run ID: {run_id}")