import os
import pandas as pd
import json
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL",
    "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
)

def recreate_rides_table():
    """Recria a tabela rides_data e importa os dados do Excel"""
    
    # Conectar ao banco PostgreSQL
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Apagar tabela se existir
            conn.execute(text("DROP TABLE IF EXISTS rides_data"))
            conn.commit()
            print("Tabela rides_data removida (se existia)")
            
            # Criar nova tabela
            create_table_sql = """
            CREATE TABLE rides_data (
                id SERIAL PRIMARY KEY,
                table_name VARCHAR(255),
                data_hash VARCHAR(255),
                ride_data TEXT,
                scraped_at TIMESTAMP,
                session_info VARCHAR(255),
                source VARCHAR(255)
            )
            """
            conn.execute(text(create_table_sql))
            conn.commit()
            print("Tabela rides_data criada com sucesso")
            
            # Ler dados do Excel
            excel_file = "CorridasConcluidas.xlsx"
            if not os.path.exists(excel_file):
                print(f"Arquivo {excel_file} não encontrado!")
                return
            
            print(f"Lendo arquivo {excel_file}...")
            df = pd.read_excel(excel_file)
            print(f"Arquivo lido: {len(df)} registros")
            
            # Converter dados para formatos serializáveis em JSON
            df_serializable = df.copy()
            for col in df_serializable.columns:
                if df_serializable[col].dtype == 'datetime64[ns]':
                    df_serializable[col] = df_serializable[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                elif df_serializable[col].dtype == 'object':
                    # Converter para string, tratando NaN
                    df_serializable[col] = df_serializable[col].fillna('').astype(str)
            
            records = df_serializable.values.tolist()
            ride_data = {
                "tableName": "corridas_concluidas",
                "newRecords": records,
                "columns": df.columns.tolist()
            }
            
            # Gerar hash dos dados
            data_string = json.dumps(ride_data, sort_keys=True, ensure_ascii=False)
            data_hash = hashlib.md5(data_string.encode('utf-8')).hexdigest()
            
            now = datetime.now()
            
            # Inserir dados na tabela
            insert_sql = """
            INSERT INTO rides_data (table_name, data_hash, ride_data, scraped_at, session_info, source)
            VALUES (:table_name, :data_hash, :ride_data, :scraped_at, :session_info, :source)
            """
            
            conn.execute(text(insert_sql), {
                'table_name': 'corridas_concluidas',
                'data_hash': data_hash,
                'ride_data': json.dumps(ride_data, ensure_ascii=False),
                'scraped_at': now,
                'session_info': 'manual_import',
                'source': 'excel_import'
            })
            conn.commit()
            
            print(f"✅ Dados importados com sucesso! {len(records)} registros")
            
            # Extrair cidades da coluna "City" (índice 15)
            cities = set()
            city_column_index = None
            
            # Encontrar o índice da coluna "City"
            columns = df.columns.tolist()
            for i, col in enumerate(columns):
                if col.lower() == 'city':
                    city_column_index = i
                    break
            
            if city_column_index is not None:
                for record in records:
                    if len(record) > city_column_index and record[city_column_index]:
                        city = str(record[city_column_index]).strip().upper()
                        if city and city != 'NAN' and city != '':
                            cities.add(city)
                
                cities_list = sorted(list(cities))
                print(f"🏙️ Cidades encontradas: {cities_list}")
                print(f"Total de cidades: {len(cities_list)}")
            else:
                print("❌ Coluna 'City' não encontrada")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    recreate_rides_table()
