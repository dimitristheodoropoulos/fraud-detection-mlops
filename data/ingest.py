import logging
import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
from pyspark.sql import functions as F

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_spark_session():
    """Δημιουργεί ένα τοπικό Spark Session."""
    return SparkSession.builder \
        .appName("FraudDetectionIngestion") \
        .master("local[*]") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()

def ingest_data(input_path, output_path):
    spark = create_spark_session()
    logger.info(f"🚀 Έναρξη Ingestion από: {input_path}")

    # 1. Ορισμός Schema (Engineering Excellence - Clean Code)
    schema = StructType([
        StructField("transaction_id", StringType(), False),
        StructField("timestamp", TimestampType(), True),
        StructField("user_id", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("merchant_category", StringType(), True),
        StructField("is_fraud", IntegerType(), True)
    ])

    try:
        # 2. Φόρτωση δεδομένων
        if not os.path.exists(input_path):
            logger.error(f"Το αρχείο {input_path} δεν βρέθηκε!")
            return

        df = spark.read.csv(input_path, header=True, schema=schema)

        # 3. Basic Cleaning (Αφαίρεση διπλοτύπων & Nulls σε κρίσιμα πεδία)
        df_clean = df.dropDuplicates(["transaction_id"]).dropna(subset=["transaction_id", "amount"])

        # 4. Feature Hint: Προσθήκη ώρας/ημέρας (βοηθάει στο Fraud Detection)
        df_final = df_clean.withColumn("hour", F.hour("timestamp")) \
                           .withColumn("day_of_week", F.dayofweek("timestamp"))

        # 5. Αποθήκευση σε Parquet (Το format που ζητάει η Sthenos)
        df_final.write.mode("overwrite").parquet(output_path)
        logger.info(f"✅ Επιτυχής αποθήκευση στο: {output_path}")

    except Exception as e:
        logger.error(f"❌ Σφάλμα: {str(e)}")
    finally:
        spark.stop()

if __name__ == "__main__":
    # Paths (θα τα φτιάξουμε στην πορεία)
    RAW_DATA = "data/raw_transactions.csv"
    PROCESSED_DATA = "data/processed_transactions.parquet"
    
    ingest_data(RAW_DATA, PROCESSED_DATA)