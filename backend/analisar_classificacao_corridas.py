import sys
import os
import asyncio
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select
from collections import defaultdict

async def analyze_ride_classification():
    """Analisa como as corridas estão sendo classificadas no banco de dados"""

    print("🔍 ANALISANDO CLASSIFICAÇÃO DAS CORRIDAS")
    print("=" * 80)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        # Contadores por tipo de tabela
        table_counts = defaultdict(int)
        record_counts = defaultdict(int)
        status_distribution = defaultdict(lambda: defaultdict(int))

        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    table_counts[table_name] += 1
                    record_counts[table_name] += len(new_records)

                    # Analisar registros individuais para ver status
                    for rec in new_records:
                        if len(rec) > 9:  # Verificar se tem dados suficientes
                            # Tentar identificar o status da corrida
                            status = None

                            # Para Completed Rides - procurar por "Completed" ou "Concluído"
                            if "Completed Rides" in table_name:
                                for idx in [9, 10, 8]:
                                    if idx < len(rec) and rec[idx]:
                                        val = str(rec[idx]).lower()
                                        if 'completed' in val or 'concluído' in val or 'concluida' in val:
                                            status = 'completed'
                                            break

                            # Para Cancelled Rides - procurar por "Cancelled"
                            elif "Cancelled Rides" in table_name:
                                for idx in [13, 14, 12]:
                                    if idx < len(rec) and rec[idx]:
                                        val = str(rec[idx]).lower()
                                        if 'cancelled' in val or 'cancelada' in val:
                                            status = 'cancelled'
                                            break

                            # Para Missed Rides - procurar por "Missed" ou "Timeout"
                            elif "Missed Rides" in table_name:
                                for idx in [4, 5]:
                                    if idx < len(rec) and rec[idx]:
                                        val = str(rec[idx]).lower()
                                        if 'missed' in val or 'timeout' in val or 'perdida' in val:
                                            status = 'missed'
                                            break

                            if status:
                                status_distribution[table_name][status] += 1

                except Exception as e:
                    continue

        # Mostrar resultados
        print("\n📈 DISTRIBUIÇÃO POR TIPO DE TABELA:")
        print("-" * 50)
        for table, count in table_counts.items():
            print(f"{table}: {count} registros, {record_counts[table]} corridas totais")

        print("\n🎯 DISTRIBUIÇÃO DE STATUS POR TABELA:")
        print("-" * 50)
        for table, statuses in status_distribution.items():
            print(f"\n{table}:")
            for status, count in statuses.items():
                print(f"  {status}: {count}")

        print("\n⚠️  ANÁLISE DE INCONSISTÊNCIAS:")
        print("-" * 50)

        # Verificar inconsistências
        for table, statuses in status_distribution.items():
            if "Completed" in table and "missed" in statuses:
                print(f"🚨 ALERTA: {table} contém {statuses['missed']} corridas classificadas como 'missed'!")
            if "Missed" in table and "completed" in statuses:
                print(f"🚨 ALERTA: {table} contém {statuses['completed']} corridas classificadas como 'completed'!")
            if "Cancelled" in table and ("completed" in statuses or "missed" in statuses):
                print(f"🚨 ALERTA: {table} contém corridas com status incorreto!")

        print("\n💡 RECOMENDAÇÕES:")
        print("- Verificar se os dados no PostgreSQL estão consistentes")
        print("- Comparar com os dados do Google Sheets")
        print("- Corrigir classificação incorreta de corridas")

if __name__ == "__main__":
    asyncio.run(analyze_ride_classification())