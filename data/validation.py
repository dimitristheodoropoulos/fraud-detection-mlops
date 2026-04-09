import pandas as pd

def validate_transaction(data: pd.DataFrame):
    # Έλεγχος αν το ποσό είναι αρνητικό (data quality)
    if (data['amount'] < 0).any():
        raise ValueError("Transaction amount cannot be negative")
    print("✅ Data validation passed.")