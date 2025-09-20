import requests
import json

def detailed_drivers_test():
    """Teste detalhado dos dados dos motoristas"""
    
    response = requests.get("http://localhost:8000/api/drivers/analytics")
    
    if response.status_code == 200:
        data = response.json()
        
        print("🚗 ANÁLISE DETALHADA DOS DADOS DOS MOTORISTAS")
        print("="*60)
        
        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            drivers_list = data['data']
            print(f"📊 Total de motoristas encontrados: {len(drivers_list)}")
            
            # Analisar primeiro motorista em detalhes
            first_driver = drivers_list[0]
            print(f"\n🔍 ESTRUTURA COMPLETA DO PRIMEIRO MOTORISTA:")
            print(json.dumps(first_driver, indent=2, ensure_ascii=False))
            
            # Procurar especificamente por campos de status
            print(f"\n🔍 BUSCA POR CAMPOS DE STATUS:")
            
            def search_for_status(obj, path=""):
                results = []
                
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # Verificar se a chave contém palavras relacionadas a status
                        if any(keyword in key.lower() for keyword in ['online', 'offline', 'status', 'active', 'inactive']):
                            results.append(f"  ✅ {current_path}: {value}")
                        
                        # Busca recursiva
                        if isinstance(value, (dict, list)):
                            results.extend(search_for_status(value, current_path))
                            
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        current_path = f"{path}[{i}]"
                        if isinstance(item, (dict, list)):
                            results.extend(search_for_status(item, current_path))
                
                return results
            
            status_fields = search_for_status(first_driver)
            
            if status_fields:
                print("CAMPOS RELACIONADOS A STATUS ENCONTRADOS:")
                for field in status_fields:
                    print(field)
            else:
                print("❌ NENHUM CAMPO RELACIONADO A STATUS ONLINE/OFFLINE ENCONTRADO")
            
            # Verificar todos os motoristas para ver se algum tem status diferente
            print(f"\n📊 ANÁLISE DE STATUS EM TODOS OS MOTORISTAS:")
            
            status_summary = {}
            online_status_summary = {}
            
            for i, driver in enumerate(drivers_list):
                driver_status_fields = search_for_status(driver)
                
                # Extrair valores de status encontrados
                for field_info in driver_status_fields:
                    if ':' in field_info:
                        field_path, field_value = field_info.split(':', 1)
                        field_path = field_path.strip().replace('✅ ', '')
                        field_value = field_value.strip()
                        
                        # Agrupar por tipo de campo
                        if field_path not in status_summary:
                            status_summary[field_path] = {}
                        
                        if field_value not in status_summary[field_path]:
                            status_summary[field_path][field_value] = 0
                        
                        status_summary[field_path][field_value] += 1
            
            if status_summary:
                print("RESUMO DOS VALORES DE STATUS ENCONTRADOS:")
                for field_path, values in status_summary.items():
                    print(f"  📋 {field_path}:")
                    for value, count in values.items():
                        print(f"    - {value}: {count} motoristas")
            else:
                print("❌ NENHUM CAMPO DE STATUS ENCONTRADO EM NENHUM MOTORISTA")
        
        else:
            print("❌ Estrutura de dados não reconhecida ou vazia")
    
    else:
        print(f"❌ Erro na requisição: {response.status_code} - {response.text}")

if __name__ == "__main__":
    detailed_drivers_test()