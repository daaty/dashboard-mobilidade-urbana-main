import requests
import json

def test_drivers_endpoints():
    """Testa os endpoints de motoristas para verificar se retornam status Online/Offline"""
    
    base_url = "http://localhost:8000"
    
    endpoints_to_test = [
        "/api/drivers/analytics",
        "/api/drivers/list",  # Se existir
        "/api/drivers/overview",  # Se existir
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n{'='*60}")
        print(f"🚗 TESTANDO ENDPOINT: {endpoint}")
        print(f"{'='*60}")
        
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analisar estrutura dos dados
                if isinstance(data, dict):
                    print(f"📊 Chaves principais: {list(data.keys())}")
                    
                    # Procurar por dados de motoristas individuais
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            print(f"\n📋 Analisando array '{key}' com {len(value)} itens:")
                            
                            # Verificar primeiro item
                            first_item = value[0]
                            if isinstance(first_item, dict):
                                print(f"  🔍 Estrutura do primeiro item: {list(first_item.keys())}")
                                
                                # Procurar campos relacionados a status online/offline
                                online_fields = []
                                for field_name, field_value in first_item.items():
                                    if any(keyword in field_name.lower() for keyword in ['online', 'offline', 'status', 'active']):
                                        online_fields.append(f"{field_name}: {field_value}")
                                
                                if online_fields:
                                    print(f"  ✅ CAMPOS RELACIONADOS A STATUS ENCONTRADOS:")
                                    for field in online_fields:
                                        print(f"    - {field}")
                                else:
                                    print(f"  ❌ Nenhum campo relacionado a status online/offline encontrado")
                                
                                # Verificar se há estruturas aninhadas
                                for field_name, field_value in first_item.items():
                                    if isinstance(field_value, dict):
                                        print(f"  📁 Estrutura aninhada '{field_name}': {list(field_value.keys())}")
                                        
                                        # Procurar status dentro de estruturas aninhadas
                                        nested_online_fields = []
                                        for nested_field, nested_value in field_value.items():
                                            if any(keyword in nested_field.lower() for keyword in ['online', 'offline', 'status', 'active']):
                                                nested_online_fields.append(f"{nested_field}: {nested_value}")
                                        
                                        if nested_online_fields:
                                            print(f"    ✅ CAMPOS DE STATUS ENCONTRADOS EM '{field_name}':")
                                            for nested_field in nested_online_fields:
                                                print(f"      - {nested_field}")
                
                elif isinstance(data, list) and len(data) > 0:
                    print(f"📊 Array direto com {len(data)} itens")
                    first_item = data[0]
                    
                    if isinstance(first_item, dict):
                        print(f"🔍 Estrutura do primeiro item: {list(first_item.keys())}")
                        
                        # Mesmo processo para arrays diretos
                        online_fields = []
                        for field_name, field_value in first_item.items():
                            if any(keyword in field_name.lower() for keyword in ['online', 'offline', 'status', 'active']):
                                online_fields.append(f"{field_name}: {field_value}")
                        
                        if online_fields:
                            print(f"✅ CAMPOS RELACIONADOS A STATUS ENCONTRADOS:")
                            for field in online_fields:
                                print(f"  - {field}")
                        else:
                            print(f"❌ Nenhum campo relacionado a status online/offline encontrado")
                            
            elif response.status_code == 404:
                print(f"❌ Endpoint não encontrado")
            else:
                print(f"❌ Erro: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"💥 Erro na requisição: {str(e)}")

if __name__ == "__main__":
    test_drivers_endpoints()