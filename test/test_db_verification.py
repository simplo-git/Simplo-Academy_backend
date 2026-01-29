import sys
import os
import requests
import time
import subprocess
from threading import Thread

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app import create_app

def run_server():
    app = create_app()
    app.run(port=5000)

def test_verification():
    # Start the server in a separate thread
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Give it a moment to start
    time.sleep(3)

    try:
        response = requests.get("http://127.0.0.1:5000/api/verify-db")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("SUCCESS: Database verification endpoint is working.")
        else:
            print("FAILURE: Endpoint returned unexpected status code.")
            
    except Exception as e:
        print(f"FAILURE: An error occurred: {e}")

if __name__ == "__main__":
    test_verification()
