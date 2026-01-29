import sys
import os
import requests
import time
from threading import Thread

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app import create_app

def run_server():
    app = create_app()
    app.run(port=5002)

def test_certificate_flow():
    # Start the server
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(3) # Wait for server

    base_url = "http://127.0.0.1:5002/api/certificates"
    
    cert_data = {
        "nome": "Test Certificate",
        "insignia": "http://example.com/badge.png",
        "descricao": "This is a test certificate",
        "data_criacao": "2024-01-27"
    }

    try:
        # 1. Create Certificate
        print("\n--- Creating Certificate ---")
        response = requests.post(base_url, json=cert_data)
        print(f"Status: {response.status_code}, Response: {response.json()}")
        if response.status_code == 201:
            cert_id = response.json()["id"]
            print(f"Certificate created with ID: {cert_id}")
        else:
            print("Failed to create certificate. Exiting.")
            return

        # 2. List Certificates
        print("\n--- Listing Certificates ---")
        response = requests.get(base_url)
        print(f"Status: {response.status_code}, Certificates count: {len(response.json())}")
        
        # 3. Get Certificate
        print("\n--- Getting Certificate ---")
        response = requests.get(f"{base_url}/{cert_id}")
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 4. Update Certificate
        print("\n--- Updating Certificate ---")
        update_data = {"nome": "Updated Certificate Name", "descricao": "Updated description"}
        response = requests.put(f"{base_url}/{cert_id}", json=update_data)
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 5. Verify Update
        print("\n--- Verifying Update ---")
        response = requests.get(f"{base_url}/{cert_id}")
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 6. Delete Certificate
        print("\n--- Deleting Certificate ---")
        response = requests.delete(f"{base_url}/{cert_id}")
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 7. Verify Deletion
        print("\n--- Verifying Deletion ---")
        response = requests.get(f"{base_url}/{cert_id}")
        print(f"Status: {response.status_code} (Expect 404)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_certificate_flow()
