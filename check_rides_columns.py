#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura da tabela rides_data
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

print("Colunas da tabela rides_data:")
print("-" * 60)

cursor.execute("""
    SELECT 
        column_name, 
        data_type
    FROM information_schema.columns
    WHERE table_name = 'rides_data'
    ORDER BY ordinal_position;
""")

for col in cursor.fetchall():
    print(f"{col['column_name']:<30} {col['data_type']}")

print("\nPrimeiro registro:")
print("-" * 60)

cursor.execute("SELECT * FROM rides_data LIMIT 1;")
record = cursor.fetchone()

if record:
    for key in record.keys():
        value = record[key]
        if isinstance(value, str) and len(value) > 100:
            value = value[:100] + "..."
        print(f"{key}: {value}")

conn.close()
