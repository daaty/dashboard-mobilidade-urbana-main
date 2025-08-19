#!/usr/bin/env python3
import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

try:
    # Conectar ao PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '148.230.73.27'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        user=os.getenv('POSTGRES_USER', 'n8n_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'n8n_pw'),
        database=os.getenv('POSTGRES_DB', 'n8n_db')
    )
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print('Todas as tabelas na base de dados:')
    for table in tables:
        print(f'  - {table[0]}')
    
    print('\n' + '='*50)
    
    # Verificar se existem outras tabelas com dados de motoristas
    cursor.execute("""
        SELECT table_name, column_name
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND (column_name LIKE '%driver%' OR column_name LIKE '%motorista%' OR table_name LIKE '%driver%')
        ORDER BY table_name, column_name
    """)
    
    columns = cursor.fetchall()
    print('Colunas/tabelas com referência a drivers/motoristas:')
    for table, column in columns:
        print(f'  - {table}.{column}')
    
    # Verificar tabelas com dados que podem ser de corridas/viagens
    print('\n' + '='*50)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND (table_name LIKE '%ride%' OR table_name LIKE '%trip%' OR table_name LIKE '%viagem%' OR table_name LIKE '%corrida%')
        ORDER BY table_name
    """)
    
    ride_tables = cursor.fetchall()
    print('Tabelas relacionadas a corridas/viagens:')
    for table in ride_tables:
        print(f'  - {table[0]}')
        
        # Contar registros em cada tabela
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{table[0]}"')
            count = cursor.fetchone()[0]
            print(f'    Registros: {count}')
        except Exception as e:
            print(f'    Erro ao contar: {e}')
    
    conn.close()
    
except Exception as e:
    print(f'Erro: {e}')
