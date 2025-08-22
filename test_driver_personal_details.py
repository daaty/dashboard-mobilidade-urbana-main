import asyncio
import asyncpg
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_driver_personal_details_data():
    """
    Testa a estrutura dos dados na tabela driver_personal_details
    """
    try:
        # Conectar ao PostgreSQL
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'dashboard_mobilidade'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        # Contar total de registros
        total_count = await conn.fetchval("SELECT COUNT(*) FROM driver_personal_details")
        print(f"Total de registros: {total_count}")
        
        # Buscar algumas amostras
        sample_data = await conn.fetch(
            "SELECT driver_id, city, personal_data, rides_history, wallet_transactions FROM driver_personal_details LIMIT 3"
        )
        
        print("\n=== AMOSTRAS DE DADOS ===")
        for i, record in enumerate(sample_data, 1):
            print(f"\n--- Driver {i} ---")
            print(f"Driver ID: {record['driver_id']}")
            print(f"Cidade: {record['city']}")
            
            # Analisar personal_data
            personal_data = record['personal_data']
            print(f"Tipo personal_data: {type(personal_data)}")
            
            if isinstance(personal_data, str):
                try:
                    personal_data = json.loads(personal_data)
                except:
                    print("Erro ao fazer parse do JSON personal_data")
                    continue
            
            if personal_data and isinstance(personal_data, dict):
                print(f"Nome: {personal_data.get('name', 'N/A')}")
                print(f"Telefone: {personal_data.get('phone', 'N/A')}")
                print(f"Email: {personal_data.get('email', 'N/A')}")
            
            # Analisar rides_history
            rides_history = record['rides_history']
            print(f"Tipo rides_history: {type(rides_history)}")
            
            if isinstance(rides_history, str):
                try:
                    rides_history = json.loads(rides_history)
                except:
                    print("Erro ao fazer parse do JSON rides_history")
                    rides_history = None
            
            if rides_history and isinstance(rides_history, list):
                total_rides = len(rides_history)
                total_earnings = sum(ride.get('fare', 0) for ride in rides_history if isinstance(ride, dict) and isinstance(ride.get('fare'), (int, float)))
                print(f"Total de corridas: {total_rides}")
                print(f"Ganhos totais: R$ {total_earnings:.2f}")
                
                # Primeira e última corrida
                if rides_history:
                    dates = [ride.get('date') for ride in rides_history if isinstance(ride, dict) and ride.get('date')]
                    if dates:
                        print(f"Período: {min(dates)} a {max(dates)}")
            
            # Analisar wallet_transactions
            wallet_transactions = record['wallet_transactions']
            print(f"Tipo wallet_transactions: {type(wallet_transactions)}")
            
            if isinstance(wallet_transactions, str):
                try:
                    wallet_transactions = json.loads(wallet_transactions)
                except:
                    print("Erro ao fazer parse do JSON wallet_transactions")
                    wallet_transactions = None
                    
            if wallet_transactions and isinstance(wallet_transactions, list):
                print(f"Transações na carteira: {len(wallet_transactions)}")
                if wallet_transactions:
                    last_balance = wallet_transactions[-1].get('balance_after', 0) if isinstance(wallet_transactions[-1], dict) else 0
                    print(f"Último saldo: R$ {last_balance:.2f}")
        
        # Estatísticas gerais
        print("\n=== ESTATÍSTICAS GERAIS ===")
        
        # Cidades únicas
        cities = await conn.fetch("SELECT DISTINCT city FROM driver_personal_details ORDER BY city")
        print(f"Cidades únicas: {len(cities)}")
        for city in cities:
            print(f"  - {city['city']}")
        
        # Drivers por cidade
        city_stats = await conn.fetch("""
            SELECT city, COUNT(*) as driver_count 
            FROM driver_personal_details 
            GROUP BY city 
            ORDER BY driver_count DESC
        """)
        print(f"\nDrivers por cidade:")
        for stat in city_stats:
            print(f"  {stat['city']}: {stat['driver_count']} drivers")
        
        await conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_driver_personal_details_data())
