import requests
import json
import pytest

# Assuming the app is running locally or we can mock, but for now let's assume we might need to run this against a running server OR import the app.
# Since I cannot easily start the server and keep it running in background for `requests` to hit it (unless I start it in a separate process),
# I will try to verify by importing the app and using `test_client`.

from app.src.routes.certificate_routes import certificate_bp
from app.src.models.certificate_model import CertificateModel
from flask import Flask

def test_certificate_model_validation():
    print("\nTesting CertificateModel validation...")
    
    # Valid case
    valid_data = {
        "nome": "Certificado Teste",
        "insignia": "url",
        "descricao": "desc",
        "data_criacao": "2024-01-01",
        "nivel": 1,
        "relacionados": [{"id": "1", "nome": "Relacionado 1"}]
    }
    cert = CertificateModel(**valid_data)
    print("Valid data passed.")

    # Invalid level (low)
    try:
        invalid_data = valid_data.copy()
        invalid_data["nivel"] = 0
        CertificateModel(**invalid_data)
        print("ERROR: Accepted nivel 0")
    except Exception as e:
        print(f"Correctly rejected nivel 0: {e}")

    # Invalid level (high)
    try:
        invalid_data = valid_data.copy()
        invalid_data["nivel"] = 4
        CertificateModel(**invalid_data)
        print("ERROR: Accepted nivel 4")
    except Exception as e:
        print(f"Correctly rejected nivel 4: {e}")

    # Invalid relacionados (wrong structure)
    try:
        invalid_data = valid_data.copy()
        invalid_data["relacionados"] = [{"wrong": "key"}]
        CertificateModel(**invalid_data)
        print("ERROR: Accepted invalid relacionados")
    except Exception as e:
        print(f"Correctly rejected invalid relacionados: {e}")

if __name__ == "__main__":
    test_certificate_model_validation()
