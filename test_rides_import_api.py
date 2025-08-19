#!/usr/bin/env python3
"""
Teste da API de importação de corridas
"""

import requests

def test_rides_import_api():
    url = "http://localhost:8000/api/import/ridesdata"
    
    # Testar com um dos arquivos de corridas
    files_to_test = [
        "CorridasConcluidas.xlsx",
        "CorridasCanceladas.xlsx",
        "CorridasPerdidas.xlsx"
    ]
    
    for file_path in files_to_test:
        try:
            print(f"\n🧪 Testando {file_path}...")
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'table_name': 'rides_data'}
                response = requests.post(url, files=files, data=data)
                
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {result}")
            
            if response.status_code == 200:
                print(f"✅ Sucesso: {result.get('imported', 0)} registros importados")
            else:
                print(f"❌ Erro: {result.get('detail', 'Erro desconhecido')}")
                
        except FileNotFoundError:
            print(f"❌ Arquivo {file_path} não encontrado")
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_rides_import_api()
