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
    
    print("🏁 Tests completed")