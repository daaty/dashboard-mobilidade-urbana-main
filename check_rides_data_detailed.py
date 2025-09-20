#!/usr/bin/env python3
"""
Script para verificar dados na tabela rides_data
"""
import asyncio
import asyncpg
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

async def check_rides_data():
    print("🔍 VERIFICANDO TABELA rides_data")
    print("=" * 50)
    
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'mobilidade_urbana'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'admin')
        )
        
        # Contar total de registros
        total = await conn.fetchval("SELECT COUNT(*) FROM rides_data")
        print(f"📊 Total de registros: {total}")
        
        # Verificar estrutura
        print("\n📋 ESTRUTURA DA TABELA:")
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'rides_data'
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            print(f"  - {col['column_name']} ({col['data_type']})")
        
        # Ver alguns registros
        print(f"\n📋 PRIMEIROS 5 REGISTROS:")
        sample = await conn.fetch("SELECT * FROM rides_data LIMIT 5")
        for i, row in enumerate(sample, 1):
            print(f"  {i}. {dict(row)}")
        
        # Verificar campos de data possíveis
        date_fields = ['data', 'date', 'created_at', 'timestamp', 'data_corrida', 'periodo']
        print(f"\n🗓️ VERIFICANDO CAMPOS DE DATA:")
        
        valid_date_field = None
        for field in date_fields:
            try:
                # Verificar se o campo existe
                test = await conn.fetchval(f"SELECT {field} FROM rides_data LIMIT 1")
                if test is not None:
                    print(f"  ✅ {field}: {test}")
                    if valid_date_field is None:
                        valid_date_field = field
            except:
                print(f"  ❌ {field}: não existe")
        
        if valid_date_field:
            print(f"\n📈 USANDO CAMPO: {valid_date_field}")
            
            # Verificar range de datas
            min_date = await conn.fetchval(f"SELECT MIN({valid_date_field}) FROM rides_data")
            max_date = await conn.fetchval(f"SELECT MAX({valid_date_field}) FROM rides_data")
            print(f"  📅 Range: {min_date} até {max_date}")
            
            # Contar por data/período
            if str(min_date).startswith('202'):  # Se for data formato YYYY
                counts = await conn.fetch(f"""
                    SELECT 
                        {valid_date_field}::text as periodo,
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' OR status = 'concluída' OR status = 'Concluída' THEN 1 ELSE 0 END) as concluidas,
                        SUM(CASE WHEN status = 'cancelled' OR status = 'cancelada' OR status = 'Cancelada' THEN 1 ELSE 0 END) as canceladas,
                        SUM(CASE WHEN status = 'lost' OR status = 'perdida' OR status = 'Perdida' THEN 1 ELSE 0 END) as perdidas
                    FROM rides_data
                    GROUP BY {valid_date_field}
                    ORDER BY {valid_date_field} DESC
                    LIMIT 15
                """)
            else:  # Formato diferente
                counts = await conn.fetch(f"""
                    SELECT 
                        {valid_date_field} as periodo,
                        COUNT(*) as total
                    FROM rides_data
                    GROUP BY {valid_date_field}
                    ORDER BY COUNT(*) DESC
                    LIMIT 15
                """)
            
            print(f"📊 DADOS POR PERÍODO:")
            for row in counts:
                print(f"  {row['periodo']}: {row['total']} registros")
        
        # Verificar campo status
        print(f"\n📊 STATUS DAS CORRIDAS:")
        status_counts = await conn.fetch("""
            SELECT status, COUNT(*) as count
            FROM rides_data
            GROUP BY status
            ORDER BY count DESC
        """)
        
        for row in status_counts:
            print(f"  {row['status']}: {row['count']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(check_rides_data())