#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
import os
from dotenv import load_dotenv

load_dotenv()

def count_real_online_drivers():
    print("=== CONTAGEM REAL DE MOTORISTAS ONLINE ===\n")
    
    # Configurar conexão com PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Contar TODOS os registros na tabela
        result = conn.execute(text("SELECT COUNT(*) FROM drivers_data"))
        total_records = result.scalar()
        print(f"📊 TOTAL DE REGISTROS NA TABELA: {total_records}")
        
        # Buscar TODOS os registros para análise
        result = conn.execute(text("""
            SELECT driver_id, name, email, additional_data, scraped_at, data_type
            FROM drivers_data 
            ORDER BY scraped_at DESC
        """))
        all_records = result.fetchall()
        
        print(f"📋 REGISTROS ENCONTRADOS: {len(all_records)}\n")
        
        online_count = 0
        online_drivers = []
        
        print("=== ANALISANDO CADA REGISTRO ===")
        for i, record in enumerate(all_records, 1):
            driver_id = record[0]
            name = record[1] 
            email = record[2]
            additional_data = record[3]
            scraped_at = record[4]
            data_type = record[5]
            
            print(f"\n{i}. REGISTRO:")
            print(f"   ID: {driver_id}")
            print(f"   Nome: {name}")
            print(f"   Email: {email}")
            print(f"   Tipo: {data_type}")
            print(f"   Data: {scraped_at}")
            
            # Verificar se tem "Online" nos dados
            has_online = False
            try:
                if additional_data:
                    if isinstance(additional_data, str):
                        data = json.loads(additional_data)
                    else:
                        data = additional_data
                    
                    # Procurar "Online" em qualquer lugar dos dados
                    data_str = str(data).lower()
                    if 'online' in data_str:
                        has_online = True
                        print(f"   ✅ ONLINE ENCONTRADO!")
                        
                        # Mostrar onde encontrou
                        if 'raw_row' in data:
                            raw_row = data['raw_row']
                            if isinstance(raw_row, list):
                                for idx, item in enumerate(raw_row):
                                    if isinstance(item, str) and item.lower() == 'online':
                                        print(f"      - Na posição {idx} do raw_row: '{item}'")
                        
                        online_count += 1
                        online_drivers.append({
                            'id': driver_id,
                            'name': name,
                            'email': email,
                            'data_type': data_type,
                            'scraped_at': scraped_at
                        })
                    else:
                        print(f"   ❌ Sem status online")
                        
            except Exception as e:
                print(f"   ⚠️  Erro ao processar: {e}")
        
        print(f"\n" + "="*50)
        print(f"🎯 RESULTADO FINAL:")
        print(f"📊 Total de registros: {total_records}")
        print(f"🟢 Motoristas com status ONLINE: {online_count}")
        print(f"🔴 Motoristas sem status online: {total_records - online_count}")
        
        print(f"\n=== LISTA DOS {online_count} MOTORISTAS ONLINE ===")
        for i, driver in enumerate(online_drivers, 1):
            print(f"{i}. {driver['name']} (ID: {driver['id']})")
            print(f"   📧 Email: {driver['email']}")
            print(f"   📅 Data: {driver['scraped_at']}")
        
        # Verificar duplicatas por nome
        names = [d['name'] for d in online_drivers if d['name']]
        unique_names = set(names)
        
        print(f"\n=== ANÁLISE DE DUPLICATAS ===")
        print(f"📝 Total de nomes: {len(names)}")
        print(f"🎯 Nomes únicos: {len(unique_names)}")
        
        if len(names) != len(unique_names):
            print("⚠️  DUPLICATAS ENCONTRADAS:")
            from collections import Counter
            name_counts = Counter(names)
            for name, count in name_counts.items():
                if count > 1:
                    print(f"   - {name}: {count} vezes")
        else:
            print("✅ Nenhuma duplicata de nome encontrada")

if __name__ == "__main__":
    count_real_online_drivers()
