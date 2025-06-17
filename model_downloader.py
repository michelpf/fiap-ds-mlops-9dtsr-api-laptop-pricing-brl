from mlflow.tracking import MlflowClient
import mlflow
import json
from datetime import datetime

print("Downloading the latest model version...")

mlflow.set_tracking_uri("https://dagshub.com/michelpf/fiap-ds-mlops-9dtsr-laptop-pricing.mlflow")

# Configurações
model_name = "laptop-pricing-model-brl"
artifact_relative_path = "model/model.pkl"

client = MlflowClient()

# 1. Buscar todas as versões do modelo
versions = client.search_model_versions(f"name='{model_name}'")

# 2. Obter a versão mais recente
latest = max(versions, key=lambda v: int(v.version))

# 3. Baixar o artefato
download_path = client.download_artifacts(
    run_id=latest.run_id,
    path=artifact_relative_path,
    dst_path="."
)

print(f"Latest model version: {latest.version}")
print(f"Model run ID: {latest.run_id}")

print(f"Writing model metadata...")

model_metadata = {
    "model_name": model_name,
    "version": latest.version,
    "run_id": latest.run_id,
    "source": latest.source,
    "downloaded_at": datetime.now().isoformat()
}

with open("model/model_metadata.json", "w") as f:
    json.dump(model_metadata, f, indent=2)

print(f"Latest model downloaded successfully in path {download_path}")