#!/usr/bin/env python3
"""Test script to verify the corrected cancellation endpoint"""

import requests
import json
from datetime import datetime

def test_cancellation_endpoint():
    """Test the corrected /api/drivers/kpis endpoint"""
    
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
            print(f"Success: {data.get('success', False)}")
            
            if 'data' in data:
                kpi_data = data['data']
                print(f"Total drivers: {kpi_data.get('total_drivers', 'N/A')}")
                print(f"Active drivers: {kpi_data.get('active_drivers', 'N/A')}")
                print(f"Corridas canceladas: {kpi_data.get('corridas_canceladas', 'N/A')}")
                print(f"Corridas perdidas: {kpi_data.get('corridas_perdidas', 'N/A')}")
                print(f"Corridas concluídas: {kpi_data.get('corridas_concluidas', 'N/A')}")
                
                # Check if we got the expected 22 cancellations
                canceladas = kpi_data.get('corridas_canceladas', 0)
                print(f"\n🔍 VALIDATION:")
                print(f"Expected cancellations: 22 (from our analysis)")
                print(f"Actual cancellations: {canceladas}")
                
                if canceladas == 22:
                    print("✅ SUCCESS: Cancellation fix is working correctly!")
                elif canceladas == 0:
                    print("❌ ISSUE: Still showing 0 cancellations")
                elif canceladas == 251:
                    print("❌ ISSUE: Still showing old fixed value of 251")
                else:
                    print(f"⚠️  UNEXPECTED: Got {canceladas} cancellations (expected 22)")
                    
            else:
                print("❌ ERROR: No 'data' field in response")
                print(f"Response: {json.dumps(data, indent=2)}")
                
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_cancellation_endpoint()