#!/usr/bin/env python3
"""
Script para analisar a estrutura da tabela passenger_personal_details
e criar endpoints para dados dos passageiros
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import Dict, List, Any

# Configuração do banco PostgreSQL
DATABASE_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def analyze_passenger_table():
    """Analisa a estrutura da tabela passenger_personal_details"""
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 ANÁLISE DA TABELA PASSENGER_PERSONAL_DETAILS")
        print("=" * 60)
        
        # 1. Verificar se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'passenger_personal_details'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Tabela 'passenger_personal_details' não encontrada!")
            return
        
        print("✅ Tabela 'passenger_personal_details' encontrada!")
        
        # 2. Obter estrutura da tabela (colunas e tipos)
        cursor.execute("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'passenger_personal_details'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 ESTRUTURA DA TABELA ({len(columns)} colunas):")
        print("-" * 60)
        
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            
            print(f"{col['column_name']:<30} {col['data_type']}{max_len:<15} {nullable}{default}")
        
        # 3. Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM passenger_personal_details;")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE REGISTROS: {total_count}")
        
        # 4. Mostrar algumas amostras de dados (primeiros 5 registros)
        if total_count > 0:
            cursor.execute("SELECT * FROM passenger_personal_details LIMIT 5;")
            samples = cursor.fetchall()
            
            print(f"\n🔬 AMOSTRA DE DADOS (primeiros 5 registros):")
            print("-" * 80)
            
            for i, sample in enumerate(samples, 1):
                print(f"\n📄 REGISTRO {i}:")
                for key, value in sample.items():
                    # Limitar strings muito longas para visualização
                    if isinstance(value, str) and len(value) > 50:
                        display_value = value[:47] + "..."
                    else:
                        display_value = value
                    print(f"  {key:<25}: {display_value}")
        
        # 5. Análise de campos importantes para dashboard
        print(f"\n🎯 ANÁLISE PARA DASHBOARD:")
        print("-" * 40)
        
        # Verificar campos comuns para dashboards
        common_fields = [
            'id', 'user_id', 'passenger_id', 'name', 'nome', 'email', 'telefone', 'phone', 
            'created_at', 'updated_at', 'data_cadastro', 'status', 'cidade', 'city',
            'age', 'idade', 'gender', 'genero', 'cpf', 'documento'
        ]
        
        available_fields = [col['column_name'] for col in columns]
        
        print("✅ Campos disponíveis para métricas:")
        for field in available_fields:
            if any(common in field.lower() for common in common_fields):
                print(f"  • {field}")
        
        # 6. Verificar campos únicos e estatísticas
        for col in columns:
            col_name = col['column_name']
            if col['data_type'] in ['varchar', 'text', 'character varying']:
                try:
                    cursor.execute(f"SELECT COUNT(DISTINCT {col_name}) as unique_count FROM passenger_personal_details WHERE {col_name} IS NOT NULL;")
                    unique_count = cursor.fetchone()['unique_count']
                    if unique_count > 0:
                        print(f"  📈 {col_name}: {unique_count} valores únicos")
                except Exception as e:
                    continue
        
        # 7. Gerar estrutura JSON para uso nos endpoints
        table_structure = {
            "table_name": "passenger_personal_details",
            "total_records": total_count,
            "columns": [
                {
                    "name": col['column_name'],
                    "type": col['data_type'],
                    "nullable": col['is_nullable'] == 'YES',
                    "max_length": col['character_maximum_length'],
                    "default": col['column_default']
                }
                for col in columns
            ],
            "sample_data": [dict(sample) for sample in samples] if total_count > 0 else []
        }
        
        # Salvar estrutura em arquivo JSON
        with open('passenger_table_structure.json', 'w', encoding='utf-8') as f:
            json.dump(table_structure, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Estrutura salva em 'passenger_table_structure.json'")
        
        cursor.close()
        conn.close()
        
        return table_structure
        
    except Exception as e:
        print(f"❌ Erro ao analisar tabela: {e}")
        return None

def suggest_dashboard_endpoints(structure):
    """Sugere endpoints baseados na estrutura da tabela"""
    if not structure:
        return
    
    print(f"\n🚀 SUGESTÕES DE ENDPOINTS PARA DASHBOARD:")
    print("=" * 50)
    
    endpoints = [
        {
            "path": "/passengers/total",
            "method": "GET", 
            "description": "Total de passageiros cadastrados"
        },
        {
            "path": "/passengers/recent", 
            "method": "GET",
            "description": "Passageiros cadastrados recentemente (últimos 30 dias)"
        },
        {
            "path": "/passengers/by-city",
            "method": "GET", 
            "description": "Distribuição de passageiros por cidade"
        },
        {
            "path": "/passengers/by-status",
            "method": "GET",
            "description": "Status dos passageiros (ativo, inativo, etc.)"
        },
        {
            "path": "/passengers/search",
            "method": "GET",
            "description": "Buscar passageiros com filtros"
        },
        {
            "path": "/passengers/analytics", 
            "method": "GET",
            "description": "Analytics gerais dos passageiros"
        }
    ]
    
    for endpoint in endpoints:
        print(f"📍 {endpoint['method']} {endpoint['path']}")
        print(f"   └─ {endpoint['description']}")
        print()

if __name__ == "__main__":
    print("🔄 Iniciando análise da tabela passenger_personal_details...")
    
    structure = analyze_passenger_table()
    
    if structure:
        suggest_dashboard_endpoints(structure)
        print("\n✅ Análise concluída! Pronto para criar os endpoints.")
    else:
        print("\n❌ Falha na análise. Verifique a conexão com o banco.")