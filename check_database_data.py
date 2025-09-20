#!/usr/bin/env python3
"""
Script para verificar se há dados reais no banco de dados
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

async def check_database_data():
    print("🔍 VERIFICANDO DADOS NO BANCO DE DADOS")
    print("=" * 50)
    
    # Conectar ao banco
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'mobilidade_urbana'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'admin')
        )
        print("✅ Conectado ao banco de dados")
        
        # Verificar tabelas existentes
        print("\n📋 TABELAS EXISTENTES:")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Verificar tabela de corridas (possíveis nomes)
        possible_tables = ['rides', 'corridas', 'viagens', 'trips']
        rides_table = None
        
        for table_name in possible_tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                print(f"\n📊 Tabela '{table_name}': {count} registros")
                if count > 0:
                    rides_table = table_name
                    break
            except:
                continue
        
        if rides_table:
            print(f"\n🎯 Usando tabela: {rides_table}")
            
            # Verificar estrutura da tabela
            print(f"\n📋 ESTRUTURA DA TABELA {rides_table}:")
            columns = await conn.fetch(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{rides_table}'
                ORDER BY ordinal_position
            """)
            
            for col in columns:
                print(f"  - {col['column_name']} ({col['data_type']})")
            
            # Verificar dados recentes
            print(f"\n📈 DADOS RECENTES ({rides_table}):")
            
            # Tentar diferentes campos de data
            date_fields = ['created_at', 'date', 'data', 'timestamp', 'data_corrida']
            date_field = None
            
            for field in date_fields:
                try:
                    recent = await conn.fetchrow(f"""
                        SELECT * FROM {rides_table} 
                        WHERE {field} >= NOW() - INTERVAL '30 days'
                        ORDER BY {field} DESC 
                        LIMIT 1
                    """)
                    if recent:
                        date_field = field
                        print(f"✅ Campo de data encontrado: {field}")
                        break
                except:
                    continue
            
            if date_field:
                # Contar registros por período
                counts = await conn.fetch(f"""
                    SELECT 
                        DATE({date_field}) as data,
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' OR status = 'concluída' THEN 1 ELSE 0 END) as concluidas,
                        SUM(CASE WHEN status = 'cancelled' OR status = 'cancelada' THEN 1 ELSE 0 END) as canceladas
                    FROM {rides_table}
                    WHERE {date_field} >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE({date_field})
                    ORDER BY DATE({date_field}) DESC
                    LIMIT 10
                """)
                
                print(f"📊 ÚLTIMOS 10 DIAS COM DADOS:")
                for row in counts:
                    print(f"  {row['data']}: {row['total']} total, {row['concluidas']} concluídas, {row['canceladas']} canceladas")
            
            else:
                print("❌ Campo de data não encontrado")
                # Mostrar alguns registros para análise
                sample = await conn.fetch(f"SELECT * FROM {rides_table} LIMIT 3")
                print("📋 AMOSTRA DE REGISTROS:")
                for row in sample:
                    print(f"  {dict(row)}")
        
        else:
            print("❌ Tabela de corridas não encontrada")
            print("📋 Tentativas feitas:", possible_tables)
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n" + "=" * 50)
    print("🔚 VERIFICAÇÃO DO BANCO CONCLUÍDA")

if __name__ == "__main__":
    asyncio.run(check_database_data())