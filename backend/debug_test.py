import asyncio
import asyncpg
from app.config.database import get_database_connection

async def test_connection():
    try:
        conn = await get_database_connection()
        
        # Verificar dados básicos
        print('=== VERIFICAÇÃO BÁSICA ===')
        result = await conn.fetchrow('SELECT COUNT(*) as total FROM drivers_data WHERE additional_data IS NOT NULL')
        print(f'Total motoristas com dados: {result[0]}')
        
        # Verificar receita total
        print('\n=== VERIFICAÇÃO RECEITA ===')
        result = await conn.fetchrow("""
            SELECT 
                SUM(CAST(additional_data->>'total_earnings' AS DECIMAL)) as receita_total,
                COUNT(*) as motoristas_com_receita
            FROM drivers_data 
            WHERE additional_data->>'total_earnings' IS NOT NULL 
            AND additional_data->>'total_earnings' != ''
            AND additional_data->>'total_earnings' != '0'
        """)
        print(f'Receita total: R$ {result[0] or 0}')
        print(f'Motoristas com receita: {result[1]}')
        
        # Verificar corridas completadas
        print('\n=== VERIFICAÇÃO CORRIDAS ===')
        result = await conn.fetchrow("""
            SELECT 
                SUM(CAST(additional_data->>'total_rides' AS INTEGER)) as corridas_total,
                COUNT(*) as motoristas_com_corridas
            FROM drivers_data 
            WHERE additional_data->>'total_rides' IS NOT NULL 
            AND additional_data->>'total_rides' != ''
            AND CAST(additional_data->>'total_rides' AS INTEGER) > 0
        """)
        print(f'Corridas totais: {result[0] or 0}')
        print(f'Motoristas com corridas: {result[1]}')
        
        # Verificar distância
        print('\n=== VERIFICAÇÃO DISTÂNCIA ===')
        result = await conn.fetchrow("""
            SELECT 
                SUM(CAST(additional_data->>'total_distance' AS DECIMAL)) as distancia_total,
                COUNT(*) as motoristas_com_distancia
            FROM drivers_data 
            WHERE additional_data->>'total_distance' IS NOT NULL 
            AND additional_data->>'total_distance' != ''
            AND CAST(additional_data->>'total_distance' AS DECIMAL) > 0
        """)
        print(f'Distância total: {result[0] or 0} km')
        print(f'Motoristas com distância: {result[1]}')
        
        # Verificar amostra de dados
        print('\n=== AMOSTRA DE DADOS ===')
        result = await conn.fetch("""
            SELECT 
                driver_id,
                additional_data->>'total_earnings' as earnings,
                additional_data->>'total_rides' as rides,
                additional_data->>'total_distance' as distance
            FROM drivers_data 
            WHERE additional_data IS NOT NULL
            LIMIT 5
        """)
        
        for row in result:
            print(f"Driver {row[0]}: Receita={row[1]}, Corridas={row[2]}, Distância={row[3]}")
        
        await conn.close()
        
    except Exception as e:
        print(f'Erro: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
