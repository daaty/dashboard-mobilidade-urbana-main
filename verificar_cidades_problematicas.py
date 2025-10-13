"""
🔍 VERIFICAR PASSAGEIROS COM PROBLEMAS DE CIDADE
Os 33 passageiros que estão sendo filtrados
"""

import asyncio
import asyncpg
import json

async def verificar_cidades_problematicas():
    print("="*100)
    print("🔍 VERIFICANDO PASSAGEIROS COM PROBLEMAS DE CIDADE")
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
        # 1. Total de passageiros
        query_total = "SELECT COUNT(*) FROM passenger_personal_details"
        total = await conn.fetchval(query_total)
        
        print(f"📊 Total de passageiros: {total}")
        print()
        
        # 2. Passageiros COM cidade válida (query do endpoint kpis)
        query_valid_city = """
        SELECT COUNT(*) 
        FROM passenger_personal_details 
        WHERE personal_data->>'city' IS NOT NULL 
        AND personal_data->>'city' != ''
        AND UPPER(personal_data->>'city') != 'N/A'
        AND TRIM(personal_data->>'city') != ''
        """
        
        valid_city = await conn.fetchval(query_valid_city)
        
        print(f"✅ Passageiros COM cidade válida: {valid_city}")
        print()
        
        # 3. Passageiros SEM cidade válida
        invalid_city = total - valid_city
        
        print(f"❌ Passageiros SEM cidade válida: {invalid_city}")
        print()
        
        # 4. Detalhar os problemas
        print("="*100)
        print("🔍 DETALHAMENTO DOS PROBLEMAS")
        print("="*100)
        print()
        
        # City IS NULL
        query_null = "SELECT COUNT(*) FROM passenger_personal_details WHERE personal_data->>'city' IS NULL"
        null_count = await conn.fetchval(query_null)
        print(f"  • City IS NULL: {null_count}")
        
        # City vazia
        query_empty = "SELECT COUNT(*) FROM passenger_personal_details WHERE personal_data->>'city' = ''"
        empty_count = await conn.fetchval(query_empty)
        print(f"  • City vazia (''): {empty_count}")
        
        # City = 'N/A'
        query_na = "SELECT COUNT(*) FROM passenger_personal_details WHERE UPPER(personal_data->>'city') = 'N/A'"
        na_count = await conn.fetchval(query_na)
        print(f"  • City = 'N/A': {na_count}")
        
        # City com espaços
        query_spaces = "SELECT COUNT(*) FROM passenger_personal_details WHERE TRIM(personal_data->>'city') = '' AND personal_data->>'city' != ''"
        spaces_count = await conn.fetchval(query_spaces)
        print(f"  • City apenas espaços: {spaces_count}")
        print()
        
        # 5. Mostrar exemplos
        print("="*100)
        print("📋 EXEMPLOS DE PASSAGEIROS FILTRADOS")
        print("="*100)
        print()
        
        query_invalid = """
        SELECT 
            passenger_id,
            personal_data,
            city
        FROM passenger_personal_details 
        WHERE NOT (
            personal_data->>'city' IS NOT NULL 
            AND personal_data->>'city' != ''
            AND UPPER(personal_data->>'city') != 'N/A'
            AND TRIM(personal_data->>'city') != ''
        )
        LIMIT 10
        """
        
        invalid_passengers = await conn.fetch(query_invalid)
        
        for row in invalid_passengers:
            p_id = row['passenger_id']
            city_field = row['city']
            personal_data = row['personal_data']
            
            if isinstance(personal_data, str):
                personal_data = json.loads(personal_data)
            
            city_in_personal = personal_data.get('city', 'N/A') if personal_data else 'N/A'
            name = personal_data.get('user_name', 'N/A') if personal_data else 'N/A'
            
            print(f"🔴 Passageiro: {p_id}")
            print(f"   Nome: {name}")
            print(f"   city (coluna): {repr(city_field)}")
            print(f"   city (personal_data): {repr(city_in_personal)}")
            print()
        
        print("="*100)
        print("🎯 CONCLUSÃO")
        print("="*100)
        print()
        print(f"Total: {total} passageiros")
        print(f"Com cidade válida: {valid_city} ({(valid_city/total*100):.1f}%)")
        print(f"Sem cidade válida: {invalid_city} ({(invalid_city/total*100):.1f}%)")
        print()
        print(f"Diferença entre /api/passengers/kpis (271) e total (304): {total - 271}")
        print(f"Passageiros sem cidade válida: {invalid_city}")
        print()
        
        if invalid_city == (total - 271):
            print("✅ CONFIRMADO! Os {invalid_city} passageiros sem cidade válida são os que estão sendo filtrados!")
        else:
            print(f"⚠️  ATENÇÃO! Há diferença: {abs(invalid_city - (total - 271))} passageiros")
        print()
    
    finally:
        await conn.close()

# Executar
asyncio.run(verificar_cidades_problematicas())
