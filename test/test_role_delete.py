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
    app.run(port=5004)

def test_role_flow_expanded():
    # Start the server
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(3) # Wait for server

    base_url = "http://127.0.0.1:5004/api/roles"
    
    role_data = {
        "nome": "Cargo Teste Delete"
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

        # 2. Delete Role
        print("\n--- Deleting Role ---")
        response = requests.delete(f"{base_url}/{role_id}")
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 3. Verify Deletion (Get List)
        print("\n--- Verifying Deletion (List) ---")
        response = requests.get(base_url)
        roles = response.json()
        found = any(r['_id'] == role_id for r in roles)
        if not found:
            print("Role successfully deleted (not found in list).")
        else:
            print("Role still exists in list!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_role_flow_expanded()
