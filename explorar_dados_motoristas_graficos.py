#!/usr/bin/env python3
"""
Script para explorar os dados disponíveis nas tabelas drivers_data e drivers_personal_data
para identificar quais gráficos podemos criar na aba de Motoristas
"""

import psycopg2
import json
from datetime import datetime
from collections import Counter, defaultdict

# String de conexão (tentando alternativa)
DATABASE_URL = "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"

def explorar_dados():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("📊 EXPLORAÇÃO DE DADOS PARA GRÁFICOS - ABA MOTORISTAS")
        print("=" * 80)
        
        # ===================================================================
        # 1. ESTRUTURA DA TABELA drivers_data
        # ===================================================================
        print("\n\n1️⃣ ESTRUTURA DA TABELA drivers_data")
        print("-" * 80)
        
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'drivers_data'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Colunas disponíveis:")
        for col, dtype, max_len in columns:
            len_info = f" ({max_len})" if max_len else ""
            print(f"   • {col}: {dtype}{len_info}")
        
        # Total de registros
        cursor.execute("SELECT COUNT(*) FROM drivers_data;")
        total_drivers_data = cursor.fetchone()[0]
        print(f"\n📊 Total de registros: {total_drivers_data}")
        
        # ===================================================================
        # 2. ANÁLISE DOS CAMPOS EM drivers_data
        # ===================================================================
        print("\n\n2️⃣ ANÁLISE DE CAMPOS PRINCIPAIS - drivers_data")
        print("-" * 80)
        
        # Buscar alguns registros para análise
        cursor.execute("""
            SELECT 
                id,
                driver_id, 
                name, 
                mobile,
                email,
                data_type,
                page_source,
                additional_data,
                scraped_at
            FROM drivers_data 
            ORDER BY scraped_at DESC
            LIMIT 10;
        """)
        
        rows = cursor.fetchall()
        
        # Analisar campos additional_data
        metricas_encontradas = defaultdict(int)
        campos_additional_data = set()
        
        print("\n🔍 Análise de 10 registros recentes:")
        for row in rows:
            id_rec, driver_id, name, mobile, email, data_type, page_source, additional_data, scraped_at = row
            
            if additional_data:
                try:
                    if isinstance(additional_data, str):
                        data = json.loads(additional_data)
                    else:
                        data = additional_data
                    
                    # Coletar todas as chaves encontradas
                    if isinstance(data, dict):
                        campos_additional_data.update(data.keys())
                        
                        # Verificar métricas específicas
                        for key in data.keys():
                            metricas_encontradas[key] += 1
                
                except Exception as e:
                    pass
        
        print(f"\n📊 Campos encontrados em additional_data ({len(campos_additional_data)} únicos):")
        for campo in sorted(campos_additional_data):
            freq = metricas_encontradas.get(campo, 0)
            print(f"   • {campo} (aparece em {freq}/10 registros)")
        
        # ===================================================================
        # 3. DADOS AGREGADOS POR page_source E data_type
        # ===================================================================
        print("\n\n3️⃣ DISTRIBUIÇÃO POR TIPO DE DADO E ORIGEM")
        print("-" * 80)
        
        cursor.execute("""
            SELECT 
                data_type,
                page_source,
                COUNT(*) as total_registros,
                COUNT(DISTINCT driver_id) as motoristas_unicos
            FROM drivers_data 
            WHERE data_type IS NOT NULL
            GROUP BY data_type, page_source
            ORDER BY total_registros DESC;
        """)
        
        tipos_dados = cursor.fetchall()
        print(f"\n📊 Tipos de dados ({len(tipos_dados)} combinações):")
        for data_type, page_source, total, unicos in tipos_dados[:15]:
            print(f"   • {data_type} / {page_source}: {unicos} motoristas únicos ({total} registros)")
        
        # ===================================================================
        # 4. ANÁLISE DE MÉTRICAS (se existirem em additional_data)
        # ===================================================================
        print("\n\n4️⃣ MÉTRICAS DE PERFORMANCE (additional_data)")
        print("-" * 80)
        
        cursor.execute("""
            SELECT additional_data
            FROM drivers_data 
            WHERE additional_data IS NOT NULL
            LIMIT 50;
        """)
        
        metricas_coletadas = {
            'total_rides': [],
            'success_rides': [],
            'cancelled_rides': [],
            'acceptance_rate': [],
            'cancellation_rate': [],
            'rating': [],
            'online_hours': [],
            'revenue': [],
            'average_rating': []
        }
        
        for (additional_data,) in cursor.fetchall():
            try:
                if isinstance(additional_data, str):
                    data = json.loads(additional_data)
                else:
                    data = additional_data
                
                if isinstance(data, dict):
                    # Tentar extrair métricas comuns (vários formatos possíveis)
                    for key in data.keys():
                        key_lower = key.lower().replace(' ', '_')
                        
                        if 'total' in key_lower and 'ride' in key_lower:
                            metricas_coletadas['total_rides'].append(data[key])
                        elif 'success' in key_lower and 'ride' in key_lower:
                            metricas_coletadas['success_rides'].append(data[key])
                        elif 'cancel' in key_lower and 'ride' in key_lower:
                            metricas_coletadas['cancelled_rides'].append(data[key])
                        elif 'acceptance' in key_lower:
                            metricas_coletadas['acceptance_rate'].append(data[key])
                        elif 'cancellation' in key_lower and 'rate' in key_lower:
                            metricas_coletadas['cancellation_rate'].append(data[key])
                        elif 'rating' in key_lower or 'avaliacao' in key_lower:
                            metricas_coletadas['rating'].append(data[key])
                        elif 'online' in key_lower and 'hour' in key_lower:
                            metricas_coletadas['online_hours'].append(data[key])
                        elif 'revenue' in key_lower or 'receita' in key_lower:
                            metricas_coletadas['revenue'].append(data[key])
            
            except Exception as e:
                pass
        
        print("\n📈 Métricas encontradas nos additional_data:")
        for metrica, valores in metricas_coletadas.items():
            if valores:
                print(f"   • {metrica}: {len(valores)} valores encontrados")
                # Mostrar exemplo
                exemplo = valores[0] if valores else None
                print(f"      Exemplo: {exemplo}")
        
        # ===================================================================
        # 5. VERIFICAR SE EXISTE TABELA drivers_personal_data
        # ===================================================================
        print("\n\n5️⃣ TABELA drivers_personal_data")
        print("-" * 80)
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'drivers_personal_data'
            );
        """)
        
        existe_personal = cursor.fetchone()[0]
        
        if existe_personal:
            print("✅ Tabela drivers_personal_data EXISTE\n")
            
            # Estrutura
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'drivers_personal_data'
                ORDER BY ordinal_position;
            """)
            
            columns_personal = cursor.fetchall()
            print("📋 Colunas disponíveis:")
            for col, dtype, max_len in columns_personal:
                len_info = f" ({max_len})" if max_len else ""
                print(f"   • {col}: {dtype}{len_info}")
            
            # Total
            cursor.execute("SELECT COUNT(*) FROM drivers_personal_data;")
            total_personal = cursor.fetchone()[0]
            print(f"\n📊 Total de registros: {total_personal}")
            
            # Amostra
            cursor.execute("""
                SELECT *
                FROM drivers_personal_data 
                LIMIT 3;
            """)
            
            print("\n🔍 Amostra de 3 registros:")
            for row in cursor.fetchall():
                print(f"   {row}")
        
        else:
            print("❌ Tabela drivers_personal_data NÃO EXISTE")
        
        # ===================================================================
        # 6. SUGESTÕES DE GRÁFICOS
        # ===================================================================
        print("\n\n" + "=" * 80)
        print("💡 SUGESTÕES DE GRÁFICOS PARA A ABA MOTORISTAS")
        print("=" * 80)
        
        sugestoes = [
            {
                "titulo": "📊 Distribuição de Motoristas por Cidade",
                "tipo": "Gráfico de Barras ou Pizza",
                "dados": "COUNT(DISTINCT driver_id) GROUP BY city",
                "endpoint": "/api/drivers/by-city-distribution"
            },
            {
                "titulo": "📈 Top 10 Motoristas por Corridas",
                "tipo": "Ranking / Gráfico de Barras Horizontal",
                "dados": "additional_data->>'total_rides' ou métricas de corridas",
                "endpoint": "/api/drivers/top-performers"
            },
            {
                "titulo": "⭐ Distribuição de Avaliações",
                "tipo": "Histograma",
                "dados": "additional_data->>'rating' ou average_rating",
                "endpoint": "/api/drivers/ratings-distribution"
            },
            {
                "titulo": "🕒 Horas Online por Motorista",
                "tipo": "Gráfico de Barras",
                "dados": "additional_data->>'online_hours'",
                "endpoint": "/api/drivers/online-hours"
            },
            {
                "titulo": "✅ Taxa de Aceitação vs Taxa de Cancelamento",
                "tipo": "Scatter Plot ou Gráfico de Dispersão",
                "dados": "acceptance_rate x cancellation_rate",
                "endpoint": "/api/drivers/acceptance-vs-cancellation"
            },
            {
                "titulo": "📅 Evolução de Cadastros ao Longo do Tempo",
                "tipo": "Gráfico de Linha",
                "dados": "COUNT(*) GROUP BY DATE(scraped_at)",
                "endpoint": "/api/drivers/registrations-timeline"
            },
            {
                "titulo": "🚗 Status dos Motoristas (Online/Offline/Unknown)",
                "tipo": "Gráfico de Pizza",
                "dados": "Dados do endpoint /api/drivers/status-kpi já existe!",
                "endpoint": "JÁ IMPLEMENTADO ✅"
            },
            {
                "titulo": "💰 Receita por Motorista",
                "tipo": "Gráfico de Barras Empilhadas",
                "dados": "additional_data->>'revenue' ou dados de corridas",
                "endpoint": "/api/drivers/revenue-analysis"
            }
        ]
        
        for i, sug in enumerate(sugestoes, 1):
            print(f"\n{i}. {sug['titulo']}")
            print(f"   Tipo: {sug['tipo']}")
            print(f"   Dados: {sug['dados']}")
            print(f"   Endpoint sugerido: {sug['endpoint']}")
        
        # ===================================================================
        # 7. EXEMPLO DE QUERY PARA CADA GRÁFICO
        # ===================================================================
        print("\n\n" + "=" * 80)
        print("🔧 QUERIES SQL SUGERIDAS")
        print("=" * 80)
        
        print("""
1. Distribuição por Cidade:
   SELECT city, COUNT(DISTINCT driver_id) as total
   FROM drivers_data
   WHERE city IS NOT NULL AND city != ''
   GROUP BY city
   ORDER BY total DESC;

2. Top Motoristas (se tiver métricas em additional_data):
   SELECT 
       name, 
       city,
       (additional_data->>'Total Rides')::int as total_rides
   FROM drivers_data
   WHERE additional_data->>'Total Rides' IS NOT NULL
   ORDER BY (additional_data->>'Total Rides')::int DESC
   LIMIT 10;

3. Cadastros ao longo do tempo:
   SELECT 
       DATE(scraped_at) as data,
       COUNT(*) as novos_cadastros
   FROM drivers_data
   GROUP BY DATE(scraped_at)
   ORDER BY data;
        """)
        
        cursor.close()
        conn.close()
        
        print("\n✅ Análise concluída!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    explorar_dados()
