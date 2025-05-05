import requests
import time

def test_api_endpoints():
    base_url = "http://localhost:8000"
    results = {}
    
    # Test real-time OBD data endpoint
    start = time.time()
    response = requests.get(f"{base_url}/api/real-time-obd-data")
    end = time.time()
    response_time = (end - start) * 1000  # convert to ms
    
    if response.status_code == 200:
        results["OBD data endpoint"] = {
            "status": "PASS",
            "response_time_ms": round(response_time, 2)
        }
    else:
        results["OBD data endpoint"] = {
            "status": "FAIL",
            "error": f"Status code: {response.status_code}"
        }
    
    # Test other endpoints
    endpoints = [
        "/api/trip-info",
        "/api/driving-behavior",
        "/api/predictive-model"
    ]
    
    for endpoint in endpoints:
        try:
            start = time.time()
            response = requests.get(f"{base_url}{endpoint}")
            end = time.time()
            response_time = (end - start) * 1000
            
            if response.status_code == 200:
                results[endpoint] = {
                    "status": "PASS",
                    "response_time_ms": round(response_time, 2)
                }
            else:
                results[endpoint] = {
                    "status": "FAIL",
                    "error": f"Status code: {response.status_code}"
                }
        except Exception as e:
            results[endpoint] = {
                "status": "ERROR",
                "error": str(e)
            }
    
    # Test efficiency score endpoint with POST request
    test_data = {
        "speed": 60.0,
        "rpm": 2500.0,
        "fuel_efficiency": 8.5,
        "engine_temp": 85.0,
        "throttle": 25.0,
        "fault_code": "None",
        "gear": 4
    }
    
    try:
        start = time.time()
        response = requests.post(f"{base_url}/api/efficiency-score", json=test_data)
        end = time.time()
        response_time = (end - start) * 1000
        
        if response.status_code == 200:
            results["efficiency-score endpoint"] = {
                "status": "PASS",
                "response_time_ms": round(response_time, 2),
                "score_result": response.json()
            }
        else:
            results["efficiency-score endpoint"] = {
                "status": "FAIL",
                "error": f"Status code: {response.status_code}"
            }
    except Exception as e:
        results["efficiency-score endpoint"] = {
            "status": "ERROR",
            "error": str(e)
        }
    
    # Print results in a readable format
    print("\nAPI Endpoint Test Results:")
    print("=" * 50)
    for endpoint, result in results.items():
        print(f"Endpoint: {endpoint}")
        for key, value in result.items():
            print(f"  {key}: {value}")
        print("-" * 50)
    
    return results

if __name__ == "__main__":
    test_api_endpoints()