"""
🔍 DESCOBRIR QUAIS 33 PASSAGEIROS A API ESTÁ FILTRANDO
"""

import asyncio
import asyncpg
import requests
import json

async def descobrir_passageiros_filtrados():
    print("="*100)
    print("🔍 DESCOBRINDO QUAIS PASSAGEIROS A API ESTÁ FILTRANDO")
    print("="*100)
    print()
    
    # Conectar ao banco
    conn = await asyncpg.connect(
        host='148.230.73.27',
        port=5432,
        database='n8n_db',
        user='n8n_user',
        password='n8n_pw'
    )
    
    try:
        # 1. Buscar TODOS os passenger_id do banco
        query_all = "SELECT passenger_id FROM passenger_personal_details ORDER BY passenger_id"
        db_passengers = await conn.fetch(query_all)
        db_passenger_ids = set(row['passenger_id'] for row in db_passengers)
        
        print(f"📊 Passageiros no BANCO: {len(db_passenger_ids)}")
        print()
        
        # 2. Buscar passenger_id da API
        print("🔍 Buscando passageiros da API...")
        resp = requests.get("http://localhost:8000/api/passengers/list", timeout=30)
        
        if resp.status_code == 200:
            api_passengers = resp.json()
            api_passenger_ids = set(p['passenger_id'] for p in api_passengers)
            
            print(f"📊 Passageiros na API: {len(api_passenger_ids)}")
            print()
            
            # 3. Encontrar diferença
            missing_in_api = db_passenger_ids - api_passenger_ids
            extra_in_api = api_passenger_ids - db_passenger_ids
            
            print("="*100)
            print("📊 ANÁLISE DE DIFERENÇAS")
            print("="*100)
            print()
            print(f"❌ Passageiros no BANCO mas NÃO na API: {len(missing_in_api)}")
            print(f"⚠️  Passageiros na API mas NÃO no BANCO: {len(extra_in_api)}")
            print()
            
            if missing_in_api:
                print("="*100)
                print(f"📋 OS {len(missing_in_api)} PASSAGEIROS FILTRADOS PELA API")
                print("="*100)
                print()
                
                # Buscar detalhes dos passageiros filtrados
                for p_id in sorted(missing_in_api)[:20]:  # Primeiros 20
                    query_details = """
                    SELECT 
                        passenger_id,
                        personal_data,
                        city,
                        CASE WHEN rides_history IS NOT NULL AND rides_history != '[]' THEN 'SIM' ELSE 'NAO' END as tem_rides,
                        extraction_source,
                        extracted_at
                    FROM passenger_personal_details
                    WHERE passenger_id = $1
                    """
                    
                    detail = await conn.fetchrow(query_details, p_id)
                    
                    if detail:
                        personal_data = detail['personal_data']
                        if isinstance(personal_data, str):
                            personal_data = json.loads(personal_data)
                        
                        name = personal_data.get('user_name', 'N/A') if personal_data else 'N/A'
                        phone = personal_data.get('user_phone', 'N/A') if personal_data else 'N/A'
                        blocked = personal_data.get('blocked', 'N/A') if personal_data else 'N/A'
                        city = detail['city']
                        tem_rides = detail['tem_rides']
                        source = detail['extraction_source']
                        
                        print(f"🔴 {p_id}")
                        print(f"   Nome: {name}")
                        print(f"   Telefone: {phone}")
                        print(f"   Cidade: {city}")
                        print(f"   Bloqueado: {blocked}")
                        print(f"   Tem rides: {tem_rides}")
                        print(f"   Source: {source}")
                        print()
                
                if len(missing_in_api) > 20:
                    print(f"... e mais {len(missing_in_api) - 20} passageiros")
                    print()
                
                # Análise de padrões
                print("="*100)
                print("🔍 ANÁLISE DE PADRÕES")
                print("="*100)
                print()
                
                # Contar por características
                blocked_count = 0
                no_rides_count = 0
                no_name_count = 0
                no_phone_count = 0
                
                for p_id in missing_in_api:
                    query_details = """
                    SELECT personal_data, rides_history
                    FROM passenger_personal_details
                    WHERE passenger_id = $1
                    """
                    
                    detail = await conn.fetchrow(query_details, p_id)
                    
                    if detail:
                        personal_data = detail['personal_data']
                        rides_history = detail['rides_history']
                        
                        if isinstance(personal_data, str):
                            personal_data = json.loads(personal_data)
                        if isinstance(rides_history, str):
                            rides_history = json.loads(rides_history)
                        
                        if personal_data:
                            if personal_data.get('blocked') == 'Yes':
                                blocked_count += 1
                            if not personal_data.get('user_name') or personal_data.get('user_name') == 'User':
                                no_name_count += 1
                            if not personal_data.get('user_phone'):
                                no_phone_count += 1
                        
                        if not rides_history or rides_history == []:
                            no_rides_count += 1
                
                print(f"📊 Passageiros BLOQUEADOS: {blocked_count}/{len(missing_in_api)}")
                print(f"📊 Passageiros SEM CORRIDAS: {no_rides_count}/{len(missing_in_api)}")
                print(f"📊 Passageiros SEM NOME: {no_name_count}/{len(missing_in_api)}")
                print(f"📊 Passageiros SEM TELEFONE: {no_phone_count}/{len(missing_in_api)}")
                print()
                
                print("="*100)
                print("🎯 CONCLUSÃO")
                print("="*100)
                print()
                
                if blocked_count == len(missing_in_api):
                    print("✅ A API está filtrando APENAS passageiros BLOQUEADOS!")
                elif no_rides_count == len(missing_in_api):
                    print("✅ A API está filtrando passageiros SEM CORRIDAS!")
                else:
                    print("⚠️  A API está usando múltiplos critérios de filtro:")
                    print(f"   - Bloqueados: {blocked_count}")
                    print(f"   - Sem corridas: {no_rides_count}")
                    print(f"   - Outros: {len(missing_in_api) - blocked_count - no_rides_count}")
                print()
            
            if extra_in_api:
                print("⚠️  ATENÇÃO! API retorna passageiros que NÃO existem no banco:")
                for p_id in sorted(extra_in_api)[:10]:
                    print(f"   - {p_id}")
                print()
        
        else:
            print(f"❌ Erro ao buscar API: {resp.status_code}")
            print(resp.text)
    
    finally:
        await conn.close()

# Executar
asyncio.run(descobrir_passageiros_filtrados())
