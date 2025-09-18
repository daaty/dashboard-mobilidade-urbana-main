#!/usr/bin/env python3
"""
Script para buscar todas as tabelas relacionadas a passageiros/passengers
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuração do banco PostgreSQL
DATABASE_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def find_passenger_tables():
    """Busca todas as tabelas relacionadas a passageiros"""
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 BUSCANDO TABELAS RELACIONADAS A PASSAGEIROS")
        print("=" * 60)
        
        # Buscar todas as tabelas que contenham 'passenger', 'user', ou 'cliente'
        cursor.execute("""
            SELECT 
                table_name,
                table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND (
                LOWER(table_name) LIKE '%passenger%' OR
                LOWER(table_name) LIKE '%user%' OR
                LOWER(table_name) LIKE '%cliente%' OR
                LOWER(table_name) LIKE '%pessoa%' OR
                LOWER(table_name) LIKE '%personal%'
            )
            ORDER BY table_name;
        """)
        
        related_tables = cursor.fetchall()
        
        if not related_tables:
            print("❌ Nenhuma tabela relacionada a passageiros encontrada!")
            
            # Listar todas as tabelas disponíveis
            print("\n📋 TODAS AS TABELAS DISPONÍVEIS:")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            all_tables = cursor.fetchall()
            
            for table in all_tables:
                print(f"  • {table['table_name']}")
            
            return []
        
        print(f"✅ Encontradas {len(related_tables)} tabelas relacionadas:")
        
        tables_info = []
        
        for table in related_tables:
            table_name = table['table_name']
            print(f"\n📋 TABELA: {table_name}")
            print("-" * 40)
            
            # Obter contagem de registros
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
                count = cursor.fetchone()['count']
                print(f"📊 Registros: {count}")
            except Exception as e:
                print(f"❌ Erro ao contar registros: {e}")
                count = 0
            
            # Obter estrutura da tabela
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            print(f"🔧 Colunas ({len(columns)}):")
            
            for col in columns:
                print(f"  • {col['column_name']} ({col['data_type']})")
            
            # Se a tabela tem dados, mostrar uma amostra
            if count > 0:
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
                    sample = cursor.fetchone()
                    
                    print(f"🔬 Amostra de dados:")
                    for key, value in sample.items():
                        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else value
                        print(f"  • {key}: {display_value}")
                        
                except Exception as e:
                    print(f"❌ Erro ao obter amostra: {e}")
            
            tables_info.append({
                'name': table_name,
                'count': count,
                'columns': [col['column_name'] for col in columns]
            })
        
        cursor.close()
        conn.close()
        
        return tables_info
        
    except Exception as e:
        print(f"❌ Erro ao buscar tabelas: {e}")
        return []

if __name__ == "__main__":
    print("🔄 Buscando tabelas de passageiros...")
    
    tables = find_passenger_tables()
    
    if tables:
        print(f"\n✅ Encontradas {len(tables)} tabelas para trabalhar!")
        print("\n🎯 RECOMENDAÇÕES:")
        
        # Escolher a melhor tabela para usar
        best_table = max(tables, key=lambda x: x['count']) if tables else None
        
        if best_table:
            print(f"📍 Tabela principal recomendada: '{best_table['name']}'")
            print(f"   └─ {best_table['count']} registros disponíveis")
            print(f"   └─ {len(best_table['columns'])} colunas")
    else:
        print("\n❌ Nenhuma tabela adequada encontrada para passageiros.")