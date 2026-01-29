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
    app.run(port=5001)

def test_user_flow():
    # Start the server
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(3) # Wait for server

    base_url = "http://127.0.0.1:5001/api/users"
    
    user_data = {
        "nome": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "setor": "IT",
        "cargo": "Dev"
    }

    try:
        # 1. Create User
        print("\n--- Creating User ---")
        response = requests.post(base_url, json=user_data)
        print(f"Status: {response.status_code}, Response: {response.json()}")
        if response.status_code == 201:
            user_id = response.json()["id"]
            print(f"User created with ID: {user_id}")
        else:
            print("Failed to create user. Exiting.")
            return

        # 2. Login
        print("\n--- Logging In ---")
        login_data = {"email": "test@example.com", "password": "password123"}
        response = requests.post(f"{base_url}/login", json=login_data)
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 3. List Users
        print("\n--- Listing Users ---")
        response = requests.get(base_url)
        print(f"Status: {response.status_code}, Users count: {len(response.json())}")

        # 4. Get User
        print("\n--- Getting User ---")
        response = requests.get(f"{base_url}/{user_id}")
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 5. Update User
        print("\n--- Updating User ---")
        update_data = {"nome": "Updated Name"}
        response = requests.put(f"{base_url}/{user_id}", json=update_data)
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 6. Delete User
        print("\n--- Deleting User ---")
        response = requests.delete(f"{base_url}/{user_id}")
        print(f"Status: {response.status_code}, Response: {response.json()}")

        # 7. Verify Deletion
        print("\n--- Verifying Deletion ---")
        response = requests.get(f"{base_url}/{user_id}")
        print(f"Status: {response.status_code} (Expect 404)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_user_flow()
