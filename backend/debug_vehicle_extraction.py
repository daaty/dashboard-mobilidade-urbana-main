import requests
import json

def debug_vehicle_extraction():
    print('🔍 DEBUG: Analisando extração de vehicle_type...')
    
    # Testar com todas as cidades para ver onde está o problema
    response = requests.get('http://localhost:8000/api/drivers/list?period=6_months&city=all&status=all&limit=100&offset=0')
    data = response.json()

    if data.get('success'):
        drivers = data.get('data', {}).get('drivers', [])
        print(f'Total de motoristas: {len(drivers)}')
        
        vehicle_stats = {}
        no_personal_data = 0
        invalid_personal_data = 0
        no_vehicle_type = 0
        
        for i, driver in enumerate(drivers):
            name = driver.get('name', 'N/A')
            personal_data_raw = driver.get('data', {}).get('personal_data')
            vehicle_type = 'Não especificado'
            
            # Debug detalhado para os primeiros 5 motoristas
            if i < 5:
                print(f'\n{i+1}. {name}:')
                print(f'   Personal data RAW: {type(personal_data_raw)} - {str(personal_data_raw)[:100]}...' if personal_data_raw else '   Personal data RAW: None')
            
            if not personal_data_raw:
                no_personal_data += 1
                if i < 5:
                    print('   ❌ Sem personal_data')
            else:
                try:
                    if isinstance(personal_data_raw, str):
                        personal_data = json.loads(personal_data_raw)
                        if i < 5:
                            print('   ✅ Personal data parseado do JSON')
                    else:
                        personal_data = personal_data_raw
                        if i < 5:
                            print('   ✅ Personal data já é dict')
                    
                    vehicle_type = personal_data.get('vehicle_type', 'Não especificado')
                    
                    if i < 5:
                        print(f'   Vehicle type extraído: "{vehicle_type}"')
                        print(f'   Todas as chaves: {list(personal_data.keys()) if isinstance(personal_data, dict) else "N/A"}')
                    
                    if not vehicle_type or vehicle_type == 'Não especificado':
                        no_vehicle_type += 1
                        
                except Exception as e:
                    invalid_personal_data += 1
                    if i < 5:
                        print(f'   ❌ Erro ao processar: {e}')
            
            # Contar veículos
            if vehicle_type not in vehicle_stats:
                vehicle_stats[vehicle_type] = 0
            vehicle_stats[vehicle_type] += 1
        
        print(f'\n📊 ESTATÍSTICAS DETALHADAS:')
        print(f'   Motoristas sem personal_data: {no_personal_data}')
        print(f'   Motoristas com personal_data inválido: {invalid_personal_data}')
        print(f'   Motoristas sem vehicle_type: {no_vehicle_type}')
        
        print(f'\n🚗 TIPOS DE VEÍCULOS ENCONTRADOS:')
        for vehicle, count in sorted(vehicle_stats.items(), key=lambda x: x[1], reverse=True):
            print(f'   {vehicle}: {count} motoristas')
            
    else:
        print(f'Erro na API: {data}')

if __name__ == "__main__":
    debug_vehicle_extraction()
