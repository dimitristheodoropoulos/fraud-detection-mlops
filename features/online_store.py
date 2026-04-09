import json
import logging
import redis
import os
from typing import Dict, Any, Optional

# Ρύθμιση του logger
logger = logging.getLogger(__name__)

class RedisFeatureStore:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Αρχικοποίηση της σύνδεσης με τη Redis χρησιμοποιώντας Connection Pool.
        """
        try:
            # Δοκιμάζουμε σύνδεση με τα παρακάτω στοιχεία
            self.pool = redis.ConnectionPool(
                host=host, 
                port=port, 
                db=db, 
                decode_responses=True 
            )
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Ping για έλεγχο
            self.client.ping()
            logger.info(f"✅ Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.critical(f"❌ Failed to connect to Redis at {host}:{port}. Error: {e}")
            raise

    def get_historical_features(self, user_id: str) -> Optional[Dict[str, Any]]:
        key = f"features:user:{user_id}"
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            logger.warning(f"⚠️ Cache miss for user_id {user_id}")
            return None
        except redis.RedisError as e:
            logger.error(f"Redis error: {e}")
            return None 

    def update_features(self, user_id: str, features: Dict[str, Any], ttl_seconds: int = 86400):
        key = f"features:user:{user_id}"
        try:
            self.client.setex(name=key, time=ttl_seconds, value=json.dumps(features))
        except redis.RedisError as e:
            logger.error(f"Failed to write features: {e}")

# --- Η ΔΙΟΡΘΩΣΗ ΕΙΝΑΙ ΕΔΩ ---
# Διαβάζουμε το REDIS_HOST από το περιβάλλον (Environment Variable).
# Αν τρέχουμε τοπικά (εκτός Docker), θα χρησιμοποιήσει το 'localhost'.
# Αν τρέχουμε μέσα σε Docker, θα του δώσουμε το 'host.docker.internal'.
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# Δημιουργία του singleton instance
feature_store = RedisFeatureStore(host=REDIS_HOST, port=6379)