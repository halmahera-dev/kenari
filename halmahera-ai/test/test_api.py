import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_all_scholarships():
    """Test endpoint untuk mengambil semua beasiswa"""
    print("🧪 Testing GET /")
    
    response = requests.get(f"{BASE_URL}/", params={"limit": 10})
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Count: {data.get('count', 0)}")
        print(f"Results: {len(data.get('results', []))} items")
        print("✅ Test passed")
    else:
        print(f"❌ Test failed: {response.text}")
    print("-" * 50)

def test_search_scholarships():
    """Test endpoint untuk pencarian beasiswa"""
    print("🧪 Testing GET /search")
    
    test_queries = [
        "computer science",
        "engineering scholarship",
        "PhD program"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        response = requests.get(f"{BASE_URL}/search", params={"query": query, "k": 5})
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Query: {data.get('query')}")
            print(f"Results: {len(data.get('results', []))} items")
            print("✅ Test passed")
        else:
            print(f"❌ Test failed: {response.text}")
        print("-" * 30)

def test_create_application():
    """Test endpoint untuk membuat aplikasi"""
    print("🧪 Testing POST /applications")
    
    payload = {
        "scholarship_id": "cc8a1b56-723d-4381-bf84-7a64f028ce39",
        "user_id": "0LscQpIu4fleX4lQosl0f3a96u2YeqTc",
        "status": "on-progress"
    }
    
    response = requests.post(f"{BASE_URL}/applications", json=payload)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Application ID: {data.get('id')}")
        print("✅ Test passed")
    else:
        print(f"❌ Test failed: {response.text}")
    print("-" * 50)

def test_create_task():
    """Test endpoint untuk membuat task"""
    print("🧪 Testing POST /tasks")
    
    payload = {
        "name": "Prepare IELTS Certificate",
        "application_id": "8d09129d-4adb-4097-a42f-21e31552e6b5",
        "description": "Get IELTS certificate with minimum score 6.5",
        "status": "pending"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", json=payload)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Task ID: {data.get('id')}")
        print("✅ Test passed")
    else:
        print(f"❌ Test failed: {response.text}")
    print("-" * 50)

def test_api_health():
    """Test koneksi ke API"""
    print("🧪 Testing API Health")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print(f"⚠️ API returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure server is running.")
    except requests.exceptions.Timeout:
        print("❌ API request timeout")
    print("-" * 50)

if __name__ == "__main__":
    print("🚀 Starting API Tests")
    print("=" * 50)
    
    test_api_health()
    test_get_all_scholarships()
    test_search_scholarships()
    test_create_application()
    test_create_task()
    
    print("🏁 Tests completed")