#!/usr/bin/env python3
"""Test script to see the full response structure"""

import requests
import json
from datetime import datetime

def test_full_response():
    """Test the complete response structure"""
    
    url = "http://localhost:8000/api/drivers/kpis"
    params = {
        "period": "30_days",
        "city": "all"
    }
    
    print(f"Testing endpoint: {url}")
    print(f"Parameters: {params}")
    print("="*50)
    
    try:
        response = requests.get(url, params=params)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("COMPLETE RESPONSE:")
            print(json.dumps(data, indent=2))
                
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_full_response()