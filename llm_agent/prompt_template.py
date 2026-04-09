FRAUD_EXPLAINER_PROMPT = """
You are a senior financial crime analyst. 
Analyze the following transaction:
- Amount: {amount} EUR
- Time: {hour}:00
- Prediction: {label}

Provide a concise, professional justification for this risk assessment.
"""