import pandas as pd
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def evaluate_model_on_production_data(model, X_test, y_test):
    """Deep dive evaluation for business stakeholders."""
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    # Financial Impact Analysis (Αυτό ζητάει η Pollfish: "move KPIs")
    false_positives = cm[0][1] # Συναλλαγές που μπλοκάραμε κατά λάθος
    lost_revenue = false_positives * 5.0 # Υποθετικό κόστος ανά FP
    
    print(f"Business Impact: Estimated ${lost_revenue} lost due to False Positives")
    
    return cm