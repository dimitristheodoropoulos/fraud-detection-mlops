import pandas as pd
import numpy as np
import os

os.makedirs('data', exist_ok=True)

n = 10000
data = {
    'amount': np.random.uniform(10, 5000, n),
    'hour': np.random.randint(0, 24, n),
    'day_of_week': np.random.randint(0, 7, n),
    'merchant_category': np.random.choice(['retail', 'online', 'food', 'travel'], n),
    'is_fraud': np.random.choice([0, 1], n, p=[0.98, 0.02])
}

df = pd.DataFrame(data)
df.to_parquet('data/processed_transactions.parquet')
print("✅ Created data/processed_transactions.parquet")