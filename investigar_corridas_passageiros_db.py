"""
🔍 INVESTIGAÇÃO PROFUNDA - CORRIDAS DE PASSAGEIROS NO BANCO DE DADOS
Verificar se os dados existem e se a lógica está correta
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from datetime import datetime, date
import json

# Configuração do banco
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dashboard_mobilidade")
engine = create_engine(DATABASE_URL)

print("="*100)
print("🔍 INVESTIGAÇÃO: CORRIDAS DE PASSAGEIROS vs RIDES_DATA")
print(f"📅 Data: {date.today()}")
print("="*100)
print()

with engine.connect() as conn:
    # =========================================================================
    # 1. VERIFICAR CORRIDAS NO RIDES_DATA (FONTE DA VERDADE)
    # =========================================================================
    print("1️⃣  VERIFICANDO RIDES_DATA (Fonte da Verdade)")
    print("-"*100)
    
    query_rides_today = text("""
        SELECT 
            id,
            ride_data->>'passenger_id' as passenger_id,
            ride_data->>'passenger_name' as passenger_name,
            ride_data->>'driver_id' as driver_id,
            ride_data->>'driver_name' as driver_name,
            ride_data->>'status' as status,
            ride_data->>'created_at' as created_at,
            ride_data->>'completed_at' as completed_at,
            created_at::date as data_corrida
        FROM rides_data
        WHERE created_at::date = CURRENT_DATE
        ORDER BY created_at DESC
    """)
    
    rides_today = conn.execute(query_rides_today).fetchall()
    
    print(f"📊 Total de corridas HOJE no rides_data: {len(rides_today)}")
    print()
    
    if len(rides_today) > 0:
        print("📋 Detalhes das corridas:")
        print(f"{'ID':<6} | {'Passageiro ID':<15} | {'Passageiro Nome':<20} | {'Motorista ID':<15} | {'Status':<15}")
        print("-"*100)
        
        passenger_ids = set()
        driver_ids = set()
        status_count = {}
        
        for ride in rides_today:
            passenger_id = ride[1]
            passenger_name = ride[2] or "N/A"
            driver_id = ride[3]
            status = ride[5] or "N/A"
            
            passenger_ids.add(passenger_id)
            driver_ids.add(driver_id)
            status_count[status] = status_count.get(status, 0) + 1
            
            print(f"{ride[0]:<6} | {passenger_id:<15} | {passenger_name[:20]:<20} | {driver_id:<15} | {status:<15}")
        
        print()
        print(f"👥 Passageiros únicos: {len(passenger_ids)}")
        print(f"🚗 Motoristas únicos: {len(driver_ids)}")
        print(f"📊 Status das corridas: {status_count}")
        print()
    
    # =========================================================================
    # 2. VERIFICAR TABELA PASSENGER_PERSONAL_DETAILS
    # =========================================================================
    print("\n2️⃣  VERIFICANDO PASSENGER_PERSONAL_DETAILS")
    print("-"*100)
    
    query_passengers_table = text("""
        SELECT 
            passenger_id,
            personal_data->>'name' as name,
            personal_data->>'email' as email,
            rides_history,
            jsonb_array_length(COALESCE(rides_history, '[]'::jsonb)) as total_rides_history,
            created_at::date as data_cadastro
        FROM passenger_personal_details
        ORDER BY created_at DESC
        LIMIT 20
    """)
    
    passengers_data = conn.execute(query_passengers_table).fetchall()
    
    print(f"📊 Total de passageiros na tabela: {len(passengers_data)}")
    print()
    
    if len(passengers_data) > 0:
        print("📋 Amostra dos passageiros:")
        print(f"{'Passenger ID':<15} | {'Nome':<25} | {'Corridas no Histórico':<20} | {'Data Cadastro':<15}")
        print("-"*100)
        
        for p in passengers_data[:10]:
            name = p[1] or "N/A"
            total_rides = p[4] or 0
            data_cadastro = p[5]
            
            print(f"{p[0]:<15} | {name[:25]:<25} | {total_rides:<20} | {str(data_cadastro):<15}")
        
        print()
    
    # =========================================================================
    # 3. VERIFICAR SE OS PASSENGER_IDs DO RIDES_DATA EXISTEM NA TABELA
    # =========================================================================
    if len(rides_today) > 0:
        print("\n3️⃣  VERIFICANDO RELACIONAMENTO RIDES_DATA ↔️ PASSENGER_PERSONAL_DETAILS")
        print("-"*100)
        
        # Pegar os passenger_ids das corridas de hoje
        passenger_ids_from_rides = list(passenger_ids)
        
        if passenger_ids_from_rides:
            # Verificar quais existem na tabela
            query_check_passengers = text("""
                SELECT 
                    passenger_id,
                    personal_data->>'name' as name,
                    jsonb_array_length(COALESCE(rides_history, '[]'::jsonb)) as total_rides,
                    created_at::date as data_cadastro
                FROM passenger_personal_details
                WHERE passenger_id = ANY(:passenger_ids)
            """)
            
            passengers_found = conn.execute(
                query_check_passengers,
                {"passenger_ids": passenger_ids_from_rides}
            ).fetchall()
            
            print(f"📊 Passageiros das corridas de HOJE encontrados na tabela: {len(passengers_found)}/{len(passenger_ids_from_rides)}")
            print()
            
            if len(passengers_found) > 0:
                print("✅ Passageiros ENCONTRADOS:")
                print(f"{'Passenger ID':<15} | {'Nome':<25} | {'Total Corridas':<15} | {'Data Cadastro':<15}")
                print("-"*100)
                for p in passengers_found:
                    print(f"{p[0]:<15} | {(p[1] or 'N/A')[:25]:<25} | {p[2]:<15} | {str(p[3]):<15}")
            
            # Verificar quais NÃO foram encontrados
            passenger_ids_found = {p[0] for p in passengers_found}
            passenger_ids_missing = passenger_ids - passenger_ids_found
            
            if passenger_ids_missing:
                print()
                print(f"❌ Passageiros NÃO ENCONTRADOS na tabela ({len(passenger_ids_missing)}):")
                for pid in passenger_ids_missing:
                    print(f"   • {pid}")
    
    # =========================================================================
    # 4. VERIFICAR A LÓGICA DO ENDPOINT /api/passengers/kpis
    # =========================================================================
    print("\n\n4️⃣  SIMULANDO LÓGICA DO ENDPOINT /api/passengers/kpis")
    print("-"*100)
    
    # Simular a query do endpoint
    query_kpis_simulation = text("""
        WITH passenger_rides AS (
            SELECT 
                passenger_id,
                personal_data,
                rides_history,
                jsonb_array_length(COALESCE(rides_history, '[]'::jsonb)) as total_rides_all_time,
                created_at
            FROM passenger_personal_details
            WHERE rides_history IS NOT NULL 
            AND jsonb_array_length(rides_history) > 0
        )
        SELECT 
            COUNT(DISTINCT passenger_id) as total_passengers,
            SUM(total_rides_all_time) as sum_total_rides
        FROM passenger_rides
        WHERE created_at::date = CURRENT_DATE
    """)
    
    kpis_result = conn.execute(query_kpis_simulation).fetchone()
    
    print(f"📊 Passageiros cadastrados HOJE: {kpis_result[0]}")
    print(f"📊 Soma de corridas históricas desses passageiros: {kpis_result[1]}")
    print()
    print("⚠️  PROBLEMA IDENTIFICADO:")
    print("   A query filtra por 'created_at::date = CURRENT_DATE'")
    print("   Isso retorna apenas passageiros CADASTRADOS hoje, não corridas de hoje!")
    print()
    
    # =========================================================================
    # 5. QUERY CORRETA - Contar corridas de HOJE do rides_history
    # =========================================================================
    print("\n5️⃣  QUERY CORRETA - Verificando rides_history com corridas de HOJE")
    print("-"*100)
    
    query_correct = text("""
        WITH passenger_rides_today AS (
            SELECT 
                ppd.passenger_id,
                ppd.personal_data->>'name' as name,
                ride->>'id' as ride_id,
                ride->>'created_at' as ride_created_at,
                ride->>'status' as ride_status
            FROM passenger_personal_details ppd,
            LATERAL jsonb_array_elements(ppd.rides_history) as ride
            WHERE (ride->>'created_at')::date = CURRENT_DATE
        )
        SELECT 
            COUNT(DISTINCT passenger_id) as passengers_with_rides_today,
            COUNT(*) as total_rides_today,
            COUNT(*) FILTER (WHERE ride_status = 'completed') as completed_rides,
            COUNT(*) FILTER (WHERE ride_status = 'cancelled') as cancelled_rides
        FROM passenger_rides_today
    """)
    
    try:
        correct_result = conn.execute(query_correct).fetchone()
        
        print("✅ RESULTADO COM QUERY CORRETA:")
        print(f"   👥 Passageiros com corridas HOJE: {correct_result[0]}")
        print(f"   📊 Total de corridas HOJE (do rides_history): {correct_result[1]}")
        print(f"   ✅ Concluídas: {correct_result[2]}")
        print(f"   ❌ Canceladas: {correct_result[3]}")
        print()
        
        # Comparar com rides_data
        print("📊 COMPARAÇÃO:")
        print(f"   rides_data: {len(rides_today)} corridas")
        print(f"   rides_history (passenger_personal_details): {correct_result[1]} corridas")
        
        if len(rides_today) != correct_result[1]:
            diff = len(rides_today) - correct_result[1]
            print(f"   ⚠️  DIFERENÇA: {abs(diff)} corridas")
            print()
            print("   💡 Possíveis causas:")
            print("   1. rides_history não está sincronizado com rides_data")
            print("   2. Algumas corridas em rides_data não foram adicionadas ao rides_history")
            print("   3. Formato de data diferente entre as tabelas")
        else:
            print(f"   ✅ CONSISTENTE! Ambas as fontes têm o mesmo número de corridas")
            
    except Exception as e:
        print(f"❌ Erro ao executar query correta: {e}")
        print("   Possível causa: rides_history pode estar vazio ou formato incorreto")
    
    # =========================================================================
    # 6. VERIFICAR FORMATO DO RIDES_HISTORY
    # =========================================================================
    print("\n\n6️⃣  VERIFICANDO FORMATO E CONTEÚDO DO RIDES_HISTORY")
    print("-"*100)
    
    query_sample_rides_history = text("""
        SELECT 
            passenger_id,
            personal_data->>'name' as name,
            rides_history,
            jsonb_array_length(COALESCE(rides_history, '[]'::jsonb)) as rides_count
        FROM passenger_personal_details
        WHERE rides_history IS NOT NULL 
        AND jsonb_array_length(rides_history) > 0
        LIMIT 3
    """)
    
    samples = conn.execute(query_sample_rides_history).fetchall()
    
    if len(samples) > 0:
        print(f"📋 Amostra de rides_history (primeiros 3 passageiros):")
        print()
        for i, sample in enumerate(samples, 1):
            print(f"   Passageiro {i}: {sample[1]} (ID: {sample[0]})")
            print(f"   Total de corridas no histórico: {sample[3]}")
            
            if sample[2]:
                rides_history = sample[2]
                if len(rides_history) > 0:
                    first_ride = rides_history[0]
                    print(f"   Primeira corrida do histórico:")
                    print(f"   {json.dumps(first_ride, indent=6)}")
            print()
    else:
        print("❌ NENHUM PASSAGEIRO COM RIDES_HISTORY ENCONTRADO!")
        print("   Isso significa que a tabela passenger_personal_details está vazia ou")
        print("   o campo rides_history não está sendo populado corretamente.")

print("\n" + "="*100)
print("✨ INVESTIGAÇÃO COMPLETA!")
print("="*100)
print()
print("📌 PRÓXIMOS PASSOS:")
print("   1. Verificar se rides_history está sendo populado corretamente")
print("   2. Corrigir a lógica do endpoint para filtrar por data da CORRIDA, não cadastro")
print("   3. Garantir sincronização entre rides_data e passenger_personal_details")
print()
