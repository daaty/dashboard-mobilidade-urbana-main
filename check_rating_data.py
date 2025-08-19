import psycopg2
import json
import os

# Configurar senha
os.environ['PGPASSWORD'] = '123mudar'

try:
    conn = psycopg2.connect(
        host='148.230.73.27', 
        user='n8n_user', 
        database='n8n', 
        password='123mudar'
    )
    cur = conn.cursor()
    
    # Buscar dados dos primeiros 5 motoristas
    cur.execute("SELECT driver_id, additional_data FROM drivers WHERE driver_id IN ('1', '2', '3', '4', '5') LIMIT 5;")
    rows = cur.fetchall()
    
    print("=== ESTRUTURA DOS DADOS DE RATING ===")
    for row in rows:
        driver_id, data = row
        print(f'\nDriver {driver_id}:')
        if data:
            # Verificar Rating direto
            if 'Rating' in data:
                print(f'  Rating direto: {data.get("Rating")}')
            
            # Verificar Rating em raw_data
            if 'raw_data' in data and data.get('raw_data') and 'Rating' in data['raw_data']:
                print(f'  Rating em raw_data: {data["raw_data"]["Rating"]}')
            
            # Listar todas as chaves disponíveis
            print(f'  Chaves disponíveis no nível principal: {list(data.keys()) if data else "None"}')
            
            # Verificar estrutura do raw_data
            if 'raw_data' in data and data.get('raw_data'):
                raw_keys = list(data['raw_data'].keys()) if isinstance(data['raw_data'], dict) else "raw_data não é dict"
                print(f'  Chaves em raw_data: {raw_keys}')
                
                # Mostrar alguns valores do raw_data para verificar nomes corretos
                if isinstance(data['raw_data'], dict):
                    for key, value in list(data['raw_data'].items())[:5]:  # Primeiros 5 itens
                        print(f'    {key}: {value}')
        else:
            print('  Dados vazios')
    
    conn.close()
    print("\n=== FIM DA VERIFICAÇÃO ===")
    
except Exception as e:
    print(f'Erro: {e}')
