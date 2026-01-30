import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print("✅ Health Check Passed:", response.json())
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        sys.exit(1)

def test_chat():
    print("\nTesting Chat Endpoint...")
    payload = {"question": "hệ thống quản lý"}
    try:
        response = requests.post(f"{BASE_URL}/api/v1/ask", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat Request Successful")
            print(f"   Answer: {data['answer'][:100]}...")
            if 'sources' in data:
                print(f"   ✅ Sources included: {len(data['sources'])} found")
                for s in data['sources']:
                    print(f"      - {s['filename']} (Page {s.get('page')})")
            else:
                print("   ❌ No sources returned!")
        else:
            print(f"❌ Chat Request Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Chat Request Error: {e}")

def test_ingest():
    print("\nTesting Ingest Endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/ingest", json={"directory_path": "./data"})
        if response.status_code == 200:
            print("✅ Ingest Request Successful:", response.json())
        else:
            print(f"❌ Ingest Request Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Ingest Request Error: {e}")

if __name__ == "__main__":
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5) 
    
    test_health()
    test_chat()
    test_ingest()
