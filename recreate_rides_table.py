#!/usr/bin/env python3
"""
Script para recriar a tabela rides_data com a estrutura original do scraper
"""

import os
import sys
import json
import pandas as pd
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do banco PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
)

# Configuração síncrona do SQLAlchemy
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Text, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base

# Base para os modelos
Base = declarative_base()

# Modelo exato como o scraper espera
class RidesData(Base):
    __tablename__ = "rides_data"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    data_hash = Column(String)
    ride_data = Column(Text)  # JSON armazenado como texto
    scraped_at = Column(DateTime)
    session_info = Column(String)
    source = Column(String)

def recreate_table():
    """Recria a tabela rides_data e importa os dados do Excel"""
    
    print("🔄 Conectando ao PostgreSQL...")
    
    # Criar engine síncrono
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Criar sessão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("🗑️ Dropando tabela rides_data se existir...")
        session.execute(text("DROP TABLE IF EXISTS rides_data"))
        session.commit()
        
        print("🏗️ Criando tabela rides_data com estrutura original...")
        Base.metadata.create_all(engine, tables=[RidesData.__table__])
        
        print("📊 Verificando se arquivo Excel existe...")
        excel_file = "CorridasConcluidas.xlsx"
        if not os.path.exists(excel_file):
            print(f"❌ Arquivo {excel_file} não encontrado!")
            return False
        
        print(f"📖 Lendo dados do arquivo {excel_file}...")
        df = pd.read_excel(excel_file)
        print(f"✅ Dados lidos: {len(df)} registros, {len(df.columns)} colunas")
        
        # Converter dados para formato JSON como o scraper faz
        print("🔄 Convertendo dados para formato JSON...")
        
        # Converter tipos para JSON serializável
        df_serializable = df.copy()
        for col in df_serializable.columns:
            if df_serializable[col].dtype == 'datetime64[ns]':
                df_serializable[col] = df_serializable[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            elif pd.api.types.is_numeric_dtype(df_serializable[col]):
                # Manter números como estão, apenas converter NaN para None
                df_serializable[col] = df_serializable[col].where(pd.notna(df_serializable[col]), None)
            else:
                # Converter para string, tratando NaN
                df_serializable[col] = df_serializable[col].astype(str).replace('nan', '')
        
        # Estrutura exata como o scraper salva
        ride_data = {
            "tableName": "corridas_concluidas",
            "newRecords": df_serializable.values.tolist()
        }
        
        # Gerar hash como o scraper faz
        data_string = json.dumps(ride_data, sort_keys=True, ensure_ascii=False)
        data_hash = hashlib.md5(data_string.encode('utf-8')).hexdigest()
        
        # Criar registro como o scraper faz
        now = datetime.now()
        entry = RidesData(
            table_name="corridas_concluidas",
            data_hash=data_hash,
            ride_data=json.dumps(ride_data, ensure_ascii=False),
            scraped_at=now,
            session_info="manual_import",
            source="excel_import"
        )
        
        print("💾 Salvando dados na tabela...")
        session.add(entry)
        session.commit()
        
        print("✅ Tabela rides_data recriada com sucesso!")
        print(f"📈 Dados importados: {len(df)} registros")
        print(f"🏷️ Tabela: corridas_concluidas")
        print(f"🔐 Hash: {data_hash[:8]}...")
        
        # Verificar se foi salvo
        count = session.execute(text("SELECT COUNT(*) FROM rides_data")).scalar()
        print(f"🔍 Verificação: {count} registro(s) na tabela rides_data")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def main():
    print("🚀 Iniciando recriação da tabela rides_data...")
    print("📋 Estrutura: Compatível com scraper original")
    print("🎯 Objetivo: Manter compatibilidade total\n")
    
    success = recreate_table()
    
    if success:
        print("\n🎉 SUCESSO! Tabela recriada e dados importados.")
        print("🔧 O scraper agora pode usar a tabela normalmente.")
    else:
        print("\n💥 FALHA na recriação da tabela.")
        sys.exit(1)

if __name__ == "__main__":
    main()
    """Importa dados do Excel para a tabela rides_data"""
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(excel_file):
            print(f"❌ Arquivo {excel_file} não encontrado")
            return False
            
        # Ler Excel
        df = pd.read_excel(excel_file)
        print(f"📊 Lido arquivo com {len(df)} registros")
        
        # Converter timestamps para strings serializáveis
        df_serializable = df.copy()
        for col in df_serializable.columns:
            if df_serializable[col].dtype == 'datetime64[ns]':
                df_serializable[col] = df_serializable[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            elif df_serializable[col].dtype == 'object':
                # Converter timestamps para string se houver
                df_serializable[col] = df_serializable[col].astype(str)
        
        # Converter para formato compatível com scraper
        records = df_serializable.values.tolist()
        ride_data = {
            "tableName": "Corridas Concluidas",
            "newRecords": records,
            "scrapedAt": datetime.now().isoformat(),
            "source": "excel_import"
        }
        
        # Conectar ao banco
        db_path = 'instance/mobilidade_urbana_dev.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Inserir dados
        import hashlib
        data_string = json.dumps(ride_data, sort_keys=True, ensure_ascii=False)
        data_hash = hashlib.md5(data_string.encode('utf-8')).hexdigest()
        
        cursor.execute('''
            INSERT INTO rides_data (table_name, data_hash, ride_data, scraped_at, session_info, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'Corridas Concluidas',
            data_hash,
            json.dumps(ride_data, ensure_ascii=False),
            datetime.now(),
            'manual_import',
            'excel_import'
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ {len(records)} registros importados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def extract_cities_from_data():
    """Extrai cidades únicas dos endereços nas corridas"""
    try:
        db_path = 'instance/mobilidade_urbana_dev.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar todos os dados de corridas
        cursor.execute('SELECT ride_data FROM rides_data WHERE table_name LIKE "%Corrida%" OR table_name LIKE "%Ride%"')
        results = cursor.fetchall()
        
        cities = set()
        
        for (ride_data_str,) in results:
            try:
                ride_data = json.loads(ride_data_str)
                records = ride_data.get('newRecords', [])
                
                for record in records:
                    # Procurar por endereços nas colunas
                    for field in record:
                        if isinstance(field, str) and any(word in field.lower() for word in ['rua', 'avenida', 'av ', 'brasil', 'mato grosso']):
                            # Extrair nome da cidade do endereço
                            parts = field.split(',')
                            for part in parts:
                                part = part.strip()
                                # Procurar por padrões de cidade
                                if len(part) > 3 and not any(prefix in part.lower() for prefix in ['rua', 'avenida', 'av ', 'número', 'casa', 'estado']):
                                    # Filtrar palavras comuns que não são cidades
                                    if not any(common in part.lower() for common in ['brasil', 'brazil', 'mato grosso', 'state of']):
                                        if part not in ['Unnamed', '--', '']:
                                            cities.add(part)
            except:
                continue
                
        conn.close()
        
        # Filtrar e limpar nomes de cidades
        clean_cities = []
        for city in cities:
            if len(city) > 2 and city.replace(' ', '').isalpha():
                clean_cities.append(city)
        
        clean_cities = sorted(list(set(clean_cities)))
        print("🏙️  Cidades encontradas:")
        for city in clean_cities[:10]:  # Mostrar apenas as primeiras 10
            print(f"   - {city}")
        
        if len(clean_cities) > 10:
            print(f"   ... e mais {len(clean_cities) - 10} cidades")
            
        return clean_cities
        
    except Exception as e:
        print(f"❌ Erro ao extrair cidades: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Recriando tabela rides_data...")
    
    # 1. Criar tabela
    engine = create_rides_table()
    
    # 2. Verificar se existe arquivo Excel para importar
    excel_files = ['CorridasConcluidas.xlsx', 'template_test.xlsx']
    for excel_file in excel_files:
        if os.path.exists(excel_file):
            print(f"📁 Importando dados de {excel_file}")
            if import_excel_to_rides_data(excel_file):
                break
    
    # 3. Extrair cidades
    print("\n🔍 Extraindo cidades dos endereços...")
    cities = extract_cities_from_data()
    
    print(f"\n✅ Processo concluído! {len(cities)} cidades encontradas.")
