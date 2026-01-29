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

def create_single_user():
    # Start the server
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(3) # Wait for server

    base_url = "http://127.0.0.1:5002/api/users"
    
    user_data = {
        "nome": "Usuario Teste Unico",
        "email": "unico@teste.com",
        "password": "senhaforte123",
        "setor": "Qualidade",
        "cargo": "Tester"
    }

    try:
        print("\n--- Creating Test User ---")
        response = requests.post(base_url, json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("SUCCESS: User created.")
        else:
            print("FAILURE: Could not create user.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_single_user()
