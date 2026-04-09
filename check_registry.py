import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()

print("--- MLflow Registry Check ---")
try:
    models = client.search_registered_models()
    if not models:
        print("❌ Κανένα μοντέλο δεν βρέθηκε στο Registry.")
    for rm in models:
        print(f"Model Name: {rm.name}")
        for mv in rm.latest_versions:
            print(f"  - Version: {mv.version}, Stage: {mv.current_stage}, Status: {mv.status}")
        # Έλεγχος για Aliases
        try:
            aliases = client.get_model_version_by_alias(rm.name, "Production")
            print(f"  - [Alias Production] points to Version: {aliases.version}")
        except:
            print("  - [Alias Production] ΔΕΝ βρέθηκε.")
except Exception as e:
    print(f"❌ Σφάλμα κατά την ανάγνωση: {e}")