import requests
import time

def test_cache_performance():
    base_url = "http://127.0.0.1:8000/properties/"
    
    print("Testing cache performance...")
    print("=" * 50)
    
    # First request (should be slower, not cached)
    start = time.time()
    response1 = requests.get(base_url)
    time1 = time.time() - start
    
    # Second request (should be faster, from cache)
    start = time.time()
    response2 = requests.get(base_url)
    time2 = time.time() - start
    
    # Third request after short delay
    time.sleep(1)
    start = time.time()
    response3 = requests.get(base_url)
    time3 = time.time() - start
    
    print(f"First request: {time1:.4f} seconds")
    print(f"Second request: {time2:.4f} seconds")
    print(f"Third request: {time3:.4f} seconds")
    print(f"\nCache speedup: {(time1/time2):.1f}x faster")
    
    # Check cache headers
    print("\nCache Headers:")
    for key, value in response2.headers.items():
        if 'cache' in key.lower() or 'expires' in key.lower():
            print(f"  {key}: {value}")
    
    # Show response
    if response2.status_code == 200:
        data = response2.json()
        print(f"\nProperties found: {data['count']}")
        print(f"Message: {data['message']}")

if __name__ == "__main__":
    test_cache_performance()