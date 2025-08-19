#!/usr/bin/env python3
"""
Teste da API de importação de motoristas
"""

import requests

def test_import_api():
    url = "http://localhost:8000/api/import/driversdata"
    file_path = "Dados Completos Motoristas.xlsx"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_import_api()
