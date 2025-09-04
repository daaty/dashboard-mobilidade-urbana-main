#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

def verificar_estrutura():
    """Verifica a estrutura da tabela e alguns dados"""
    
    # Conectar ao banco
    conn = sqlite3.connect('drivers_data.db')
    cursor = conn.cursor()
    
    print("=== VERIFICANDO ESTRUTURA DO BANCO ===\n")
    
    # Verificar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tabelas disponíveis:")
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n=== ESTRUTURA DA TABELA drivers_data ===")
    cursor.execute("PRAGMA table_info(drivers_data);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    print("\n=== CONTAGEM TOTAL DE REGISTROS ===")
    cursor.execute("SELECT COUNT(*) FROM drivers_data;")
    total = cursor.fetchone()[0]
    print(f"Total de registros: {total}")
    
    print("\n=== CONTAGEM POR PAGE_SOURCE ===")
    cursor.execute("SELECT page_source, COUNT(*) FROM drivers_data GROUP BY page_source;")
    pages = cursor.fetchall()
    for page, count in pages:
        print(f"  - {page}: {count}")
    
    print("\n=== ALGUNS DADOS DE EXEMPLO ===")
    cursor.execute("SELECT driver_id, name, page_source FROM drivers_data LIMIT 3;")
    examples = cursor.fetchall()
    for ex in examples:
        print(f"  - ID: {ex[0]}, Nome: {ex[1]}, Página: {ex[2]}")
    
    conn.close()

if __name__ == "__main__":
    verificar_estrutura()
