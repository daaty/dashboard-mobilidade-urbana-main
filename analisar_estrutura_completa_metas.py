#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica estrutura real da tabela metas_progressivas
"""

import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

load_dotenv('backend/.env.production')

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor(cursor_factory=DictCursor)

print("="*80)
print("ESTRUTURA DA TABELA: metas_progressivas")
print("="*80 + "\n")

# Colunas
cursor.execute("""
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_name = 'metas_progressivas'
    ORDER BY ordinal_position;
""")

print("COLUNAS:")
for col in cursor.fetchall():
    print(f"  - {col['column_name']:<30} {col['data_type']:<20} (Nullable: {col['is_nullable']}, Default: {col['column_default']})")

# Amostra de dados
print("\n" + "="*80)
print("AMOSTRA DE DADOS (3 registros):")
print("="*80 + "\n")

cursor.execute("SELECT * FROM metas_progressivas LIMIT 3;")
for i, row in enumerate(cursor.fetchall(), 1):
    print(f"\nRegistro {i}:")
    for key, value in dict(row).items():
        print(f"  {key}: {value}")

conn.close()
