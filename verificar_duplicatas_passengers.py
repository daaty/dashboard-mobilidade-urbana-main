"""
🔍 VERIFICAR DUPLICATAS NA TABELA PASSENGER_PERSONAL_DETAILS
Checar se os 304 registros são passageiros únicos
"""

import asyncio
import asyncpg
import json
from collections import Counter

async def verificar_duplicatas():
    print("="*100)
    print("🔍 VERIFICANDO DUPLICATAS NA TABELA PASSENGER_PERSONAL_DETAILS")
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
        # 1. Contar total de registros
        query_total = "SELECT COUNT(*) FROM passenger_personal_details"
        total_records = await conn.fetchval(query_total)
        
        print(f"📊 Total de REGISTROS na tabela: {total_records}")
        print()
        
        # 2. Contar passenger_id distintos
        query_distinct = "SELECT COUNT(DISTINCT passenger_id) FROM passenger_personal_details"
        distinct_passengers = await conn.fetchval(query_distinct)
        
        print(f"✅ Total de PASSENGER_ID ÚNICOS: {distinct_passengers}")
        print()
        
        # 3. Verificar se tem duplicatas
        duplicates = total_records - distinct_passengers
        
        if duplicates > 0:
            print(f"⚠️  ENCONTRADAS {duplicates} DUPLICATAS!")
            print()
            
            # 4. Listar os passenger_id duplicados
            query_duplicates = """
            SELECT passenger_id, COUNT(*) as count
            FROM passenger_personal_details
            GROUP BY passenger_id
            HAVING COUNT(*) > 1
            ORDER BY count DESC, passenger_id
            """
            
            duplicate_rows = await conn.fetch(query_duplicates)
            
            print("="*100)
            print("📋 PASSENGER_IDS DUPLICADOS")
            print("="*100)
            print()
            
            for row in duplicate_rows:
                p_id = row['passenger_id']
                count = row['count']
                
                print(f"🔴 Passenger ID: {p_id} - {count} registros")
                
                # Buscar detalhes de cada registro duplicado
                query_details = """
                SELECT 
                    passenger_id,
                    personal_data,
                    city,
                    CASE WHEN rides_history IS NOT NULL THEN 'SIM' ELSE 'NAO' END as tem_rides,
                    extraction_source,
                    extracted_at
                FROM passenger_personal_details
                WHERE passenger_id = $1
                ORDER BY extracted_at DESC
                """
                
                details = await conn.fetch(query_details, p_id)
                
                for i, detail in enumerate(details, 1):
                    personal_data = detail['personal_data']
                    if isinstance(personal_data, str):
                        personal_data = json.loads(personal_data)
                    
                    name = personal_data.get('user_name', 'N/A') if personal_data else 'N/A'
                    phone = personal_data.get('user_phone', 'N/A') if personal_data else 'N/A'
                    city = detail['city']
                    tem_rides = detail['tem_rides']
                    source = detail['extraction_source']
                    extracted_at = detail['extracted_at']
                    
                    print(f"   {i}. Nome: {name} | Telefone: {phone}")
                    print(f"      Cidade: {city} | Rides: {tem_rides}")
                    print(f"      Source: {source} | Extraído em: {extracted_at}")
                    print()
                
                print()
        else:
            print("✅ NÃO HÁ DUPLICATAS! Todos os passenger_id são únicos.")
            print()
        
        # 5. Verificar distribuição por cidade
        query_cities = """
        SELECT city, COUNT(*) as count
        FROM passenger_personal_details
        GROUP BY city
        ORDER BY count DESC
        """
        
        cities = await conn.fetch(query_cities)
        
        print("="*100)
        print("🏙️  DISTRIBUIÇÃO POR CIDADE")
        print("="*100)
        print()
        
        total_cities = len(cities)
        
        for city_row in cities:
            city = city_row['city']
            count = city_row['count']
            percentage = (count / total_records) * 100
            
            print(f"📍 {city}: {count} passageiros ({percentage:.1f}%)")
        
        print()
        print(f"📊 Total de CIDADES: {total_cities}")
        print()
        
        # 6. Verificar se a API está filtrando algo
        print("="*100)
        print("🎯 COMPARAÇÃO COM API")
        print("="*100)
        print()
        print(f"Banco de dados:")
        print(f"  - Total de registros: {total_records}")
        print(f"  - Passageiros únicos: {distinct_passengers}")
        print(f"  - Cidades: {total_cities}")
        print()
        print(f"API retorna:")
        print(f"  - Total de passageiros: 271")
        print(f"  - Cidades: 4")
        print()
        
        diff_passengers = total_records - 271
        diff_cities = total_cities - 4
        
        if diff_passengers > 0:
            print(f"⚠️  DIFERENÇA: {diff_passengers} passageiros")
            print()
            print("Possíveis causas:")
            print("  1. API está filtrando registros duplicados")
            print("  2. API está aplicando algum filtro (status, cidade, etc)")
            print("  3. API está removendo registros inválidos/incompletos")
            print()
        
        if diff_cities > 0:
            print(f"⚠️  DIFERENÇA: {diff_cities} cidades a mais no banco")
            print()
            
            # Mostrar quais cidades podem estar sendo filtradas
            print("Cidades no banco:")
            for city_row in cities:
                print(f"  - {city_row['city']}")
            print()
        
        # 7. Verificar se tem registros sem city ou com city NULL
        query_no_city = """
        SELECT COUNT(*) 
        FROM passenger_personal_details
        WHERE city IS NULL OR city = ''
        """
        
        no_city = await conn.fetchval(query_no_city)
        
        if no_city > 0:
            print(f"⚠️  {no_city} passageiros SEM CIDADE definida!")
            print()
        
    finally:
        await conn.close()

# Executar
asyncio.run(verificar_duplicatas())
