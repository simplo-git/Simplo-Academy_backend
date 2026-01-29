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
    app.run(port=5003)

def test_role_flow():
    # Start the server
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(3) # Wait for server

    base_url = "http://127.0.0.1:5003/api/roles"
    
    role_data = {
        "nome": "Cargo Teste"
    }

    try:
        # 1. Create Role
        print("\n--- Creating Role ---")
        response = requests.post(base_url, json=role_data)
        print(f"Status: {response.status_code}, Response: {response.json()}")
        if response.status_code == 201:
            role_id = response.json()["id"]
        else:
            print("Failed to create role. Exiting.")
            return

        # 2. List Roles
        print("\n--- Listing Roles ---")
        response = requests.get(base_url)
        print(f"Status: {response.status_code}, Count: {len(response.json())}")

        # 3. Update Role
        print("\n--- Updating Role ---")
        update_data = {"nome": "Cargo Editado"}
        response = requests.put(f"{base_url}/{role_id}", json=update_data)
        print(f"Status: {response.status_code}, Response: {response.json()}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_role_flow()
