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

# Configuração do banco PostgreSQL - usando driver síncrono
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
).replace("postgresql+asyncpg://", "postgresql://")

# Configuração síncrona do SQLAlchemy
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Text
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
        
        # Extrair cidades reais
        if 'City' in df.columns:
            cities = df['City'].dropna().unique().tolist()
            cities = [str(city).strip() for city in cities if city and str(city).strip() != '']
            print(f"🏙️ Cidades extraídas: {cities}")
        
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
        print("📊 O dashboard pode extrair cidades reais dos dados.")
    else:
        print("\n💥 FALHA na recriação da tabela.")
        sys.exit(1)

if __name__ == "__main__":
    main()
