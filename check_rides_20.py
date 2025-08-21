#!/usr/bin/env python3
"""
Script para verificar corridas do dia 20/08/2025 na tabela rides_data do PostgreSQL na VPS
"""
import psycopg2
from datetime import datetime, timedelta

def check_rides_20():
    # String de conexão PostgreSQL na VPS
    DATABASE_URL = 'postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db'
    print(f'🔗 Conectando ao PostgreSQL na VPS: 148.230.73.27')
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        print("✅ Conectado ao PostgreSQL na VPS!")
        
        # Verificar se a tabela rides_data existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'rides_data'
            );
        """)
        table_exists = cursor.fetchone()[0]
        print(f"📋 Tabela 'rides_data' existe: {table_exists}")
        
        if not table_exists:
            print("❌ Tabela 'rides_data' não encontrada!")
            # Verificar outras tabelas relacionadas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name LIKE '%ride%' OR table_name LIKE '%corrida%'
                ORDER BY table_name;
            """)
            similar_tables = cursor.fetchall()
            if similar_tables:
                print("🔍 Tabelas similares encontradas:")
                for table in similar_tables:
                    print(f"  • {table[0]}")
            conn.close()
            return
        
        # Verificar estrutura da tabela
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'rides_data'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print(f"\n📊 Estrutura da tabela 'rides_data':")
        for col in columns:
            print(f"  • {col[0]}: {col[1]}")
        
        # Verificar total de registros na tabela
        cursor.execute("SELECT COUNT(*) FROM rides_data;")
        total_records = cursor.fetchone()[0]
        print(f"\n📈 Total de registros na tabela: {total_records:,}")
        
        # Verificar todos os registros da tabela
        cursor.execute("""
            SELECT 
                id,
                table_name,
                ride_data,
                scraped_at,
                session_info,
                source
            FROM rides_data 
            ORDER BY scraped_at DESC;
        """)
        todos_registros = cursor.fetchall()
        
        print(f"\n📋 Todos os registros da tabela rides_data:")
        import json
        corridas_20_count = 0
        corridas_detalhadas = []
        
        for registro in todos_registros:
            id_reg = registro[0]
            table_name = registro[1]
            ride_data_str = registro[2]
            scraped_at = registro[3]
            session_info = registro[4]
            source = registro[5]
            
            print(f"\n🔍 Registro ID: {id_reg}")
            print(f"  • Table Name: {table_name}")
            print(f"  • Scraped At: {scraped_at}")
            print(f"  • Session Info: {session_info}")
            print(f"  • Source: {source}")
            
            # Tentar analisar ride_data como JSON
            try:
                if ride_data_str:
                    ride_data = json.loads(ride_data_str)
                    print(f"  • Ride Data: {type(ride_data)} com {len(ride_data) if isinstance(ride_data, (list, dict)) else 'N/A'} itens")
                    
                    # Se for uma lista de corridas
                    if isinstance(ride_data, list):
                        for idx, corrida in enumerate(ride_data[:3]):  # Mostrar apenas as primeiras 3
                            if isinstance(corrida, dict):
                                dt_corrida = corrida.get('dt_corrida', corrida.get('hora', 'N/A'))
                                nome = corrida.get('nome', 'N/A')
                                grupo = corrida.get('grupo', 'N/A')
                                cidade = corrida.get('cidade', 'N/A')
                                print(f"    - Corrida {idx+1}: {dt_corrida} | {nome} | {grupo} | {cidade}")
                                
                                # Verificar se é do dia 20
                                if '2025-08-20' in str(dt_corrida):
                                    corridas_20_count += 1
                                    corridas_detalhadas.append(corrida)
                    
                    # Se for um dicionário único
                    elif isinstance(ride_data, dict):
                        dt_corrida = ride_data.get('dt_corrida', ride_data.get('hora', 'N/A'))
                        nome = ride_data.get('nome', 'N/A')
                        grupo = ride_data.get('grupo', 'N/A')
                        cidade = ride_data.get('cidade', 'N/A')
                        print(f"    - Corrida única: {dt_corrida} | {nome} | {grupo} | {cidade}")
                        
                        # Verificar se é do dia 20
                        if '2025-08-20' in str(dt_corrida):
                            corridas_20_count += 1
                            corridas_detalhadas.append(ride_data)
                else:
                    print(f"  • Ride Data: vazio")
                    
            except json.JSONDecodeError as e:
                print(f"  • Ride Data: erro ao decodificar JSON - {e}")
                print(f"  • Conteúdo bruto (primeiros 200 chars): {ride_data_str[:200] if ride_data_str else 'vazio'}")
        
        print(f"\n🎯 RESULTADO: Encontradas {corridas_20_count} corridas do dia 20/08/2025")
        
        if corridas_detalhadas:
            print(f"\n📋 Detalhes das corridas do dia 20:")
            for idx, corrida in enumerate(corridas_detalhadas[:10]):  # Mostrar até 10
                dt_corrida = corrida.get('dt_corrida', corrida.get('hora', 'N/A'))
                nome = corrida.get('nome', 'N/A')
                grupo = corrida.get('grupo', 'N/A')
                cidade = corrida.get('cidade', 'N/A')
                local = corrida.get('local', 'N/A')
                destino = corrida.get('destino', 'N/A')
                print(f"  {idx+1}. {dt_corrida} | {nome} | {grupo} | {cidade} | {local} → {destino}")
        
        # Verificar datas de scraping
        cursor.execute("""
            SELECT 
                DATE(scraped_at) as data_scraping,
                COUNT(*) as registros_scrapados
            FROM rides_data 
            GROUP BY DATE(scraped_at)
            ORDER BY data_scraping DESC;
        """)
        scraping_dates = cursor.fetchall()
        
        print(f"\n� Datas de scraping:")
        for data in scraping_dates:
            print(f"  • {data[0]}: {data[1]} registros")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao conectar/consultar PostgreSQL: {e}")

if __name__ == "__main__":
    check_rides_20()
