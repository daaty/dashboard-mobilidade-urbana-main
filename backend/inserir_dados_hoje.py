import sys
import os
import asyncio
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData

async def insert_test_data_today():
    """Insere dados de teste para hoje"""

    # Dados de teste para hoje
    hoje = datetime.now()
    hoje_str = hoje.strftime("%Y-%m-%d %H:%M:%S")

    # Dados de exemplo - corridas concluídas hoje
    test_data_completed = {
        "tableName": "Completed Rides",
        "newRecords": [
            [
                "TEST001",  # ID
                "--",       # Campo vazio
                "João Silva",  # Nome passageiro
                "Centro",   # Origem
                "+5566999999999",  # Telefone
                "Test Driver",  # Motorista
                "Av. Principal, 123",  # Endereço origem
                hoje_str,   # Data conclusão
                hoje_str,   # Data solicitação
                "POPULAR",  # Tipo
                "Completed", # Status
                "--",       # Campo vazio
                "--",       # Campo vazio
                "5",        # Valor
                "-",        # Campo vazio
                "-"         # Campo vazio
            ],
            [
                "TEST002",
                "--",
                "Maria Santos",
                "Bairro Novo",
                "+5566999999998",
                "Test Driver 2",
                "Rua Secundária, 456",
                hoje_str,
                hoje_str,
                "POPULAR",
                "Completed",
                "--",
                "--",
                "8",
                "-",
                "-"
            ]
        ]
    }

    # Dados de exemplo - corridas canceladas hoje
    test_data_cancelled = {
        "tableName": "Cancelled Rides",
        "newRecords": [
            [
                "TEST003",
                "--",
                "Pedro Oliveira",
                "18318166",
                "+5566999999997",
                "Test Driver 3",
                "POPULAR",
                "Rua Cancelada, 789",
                "Av. Destino, 101",
                "--",
                "--",
                hoje_str,
                "Cliente desistiu",
                "Cancelled by Customer",
                "--",
                "--",
                "Book Ride"
            ]
        ]
    }

    async with SessionLocal() as session:
        try:
            # Inserir dados de corridas concluídas
            ride_completed = RidesData(
                table_name="Completed Rides",
                ride_data=json.dumps(test_data_completed),
                scraped_at=hoje,
                source="test_data"
            )
            session.add(ride_completed)

            # Inserir dados de corridas canceladas
            ride_cancelled = RidesData(
                table_name="Cancelled Rides",
                ride_data=json.dumps(test_data_cancelled),
                scraped_at=hoje,
                source="test_data"
            )
            session.add(ride_cancelled)

            await session.commit()

            print("✅ Dados de teste inseridos com sucesso!")
            print(f"📅 Data dos registros: {hoje_str}")
            print("📊 2 corridas concluídas + 1 cancelada inseridas")

        except Exception as e:
            await session.rollback()
            print(f"❌ Erro ao inserir dados: {e}")

if __name__ == "__main__":
    asyncio.run(insert_test_data_today())