#!/usr/bin/env python3
"""
Teste da nova importação com todos os dados preservados
"""

import requests
import os

def test_import():
    """Testa a importação completa de dados de motoristas"""
    
    # Arquivo para importar
    file_path = "Dados Completos Motoristas.xlsx"
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo {file_path} não encontrado!")
        return
    
    print(f"📁 Importando arquivo: {file_path}")
    
    # Fazer upload para API
    url = "http://localhost:8000/api/import/driversdata"
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        data = {'table_name': 'drivers_data'}
        
        try:
            response = requests.post(url, files=files, data=data)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sucesso!")
                print(f"   📈 Importados: {result.get('imported', 0)}")
                print(f"   📄 Total linhas: {result.get('total_rows', 0)}")
                print(f"   ⚠️ Erros: {result.get('errors', 0)}")
                
                if result.get('error_details'):
                    print(f"   🔍 Detalhes dos erros:")
                    for error in result['error_details']:
                        print(f"      - {error}")
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")

def test_analytics():
    """Testa o endpoint de analytics"""
    
    print("\n🔍 Testando endpoint de analytics...")
    
    try:
        response = requests.get("http://localhost:8000/api/drivers/analytics")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analytics funcionando!")
            print(f"   📊 Total de registros: {result.get('total_records', 0)}")
            
            drivers = result.get('drivers', [])
            if drivers:
                print(f"   👤 Primeiro motorista: {drivers[0]['name']} (ID: {drivers[0]['driver_id']})")
                
                # Mostrar estrutura dos dados
                if 'data' in drivers[0] and drivers[0]['data']:
                    data = drivers[0]['data']
                    print(f"   📋 Estrutura dos dados:")
                    print(f"      - raw_data: {len(data.get('raw_data', {})) if data.get('raw_data') else 0} campos")
                    print(f"      - metrics: {data.get('metrics', {})}")
                    print(f"      - profile: {data.get('profile', {})}")
                    
                    if data.get('raw_data'):
                        print(f"   🔧 Campos originais disponíveis:")
                        for key, value in list(data['raw_data'].items())[:5]:
                            print(f"      - {key}: {value}")
                        if len(data['raw_data']) > 5:
                            print(f"      ... e mais {len(data['raw_data']) - 5} campos")
        else:
            print(f"❌ Erro no analytics: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição de analytics: {e}")

if __name__ == "__main__":
    print("🚀 Teste de Importação Completa de Dados de Motoristas")
    print("=" * 60)
    
    # Primeiro fazer a importação
    test_import()
    
    # Depois testar os analytics
    test_analytics()
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
