def get_historical_features(user_id: str):
    """
    Mock-up of a feature store retrieval.
    In production, this would query a database like Redis or Snowflake.
    """
    return {"avg_spend_7d": 150.0, "total_trans_24h": 5}