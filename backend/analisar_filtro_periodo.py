import sys
import os
import asyncio
import json
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select

def extract_datetime_from_record(rec, index):
    """Extrai data/hora de um registro, lidando com AMBOS os formatos (scraper + frontend)"""
    if index >= len(rec):
        return None

    value = str(rec[index]).strip()

    # Formato do scraper: "202508202025-08-20 16:59:50"
    scraper_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", value)
    if scraper_match:
        return scraper_match.group(1)

    # Formato do frontend: "2025-08-20 16:59:50" (sem prefixo)
    frontend_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", value)
    if frontend_match:
        return frontend_match.group(1)

    return None

def get_period_filter(periodo: str):
    """Retorna os filtros de data baseados no período selecionado"""
    now = datetime.now()

    if periodo == "hoje":
        dt_ini = now.replace(hour=0, minute=0, second=0, microsecond=0)
        dt_fim = now
    elif periodo == "7d":
        dt_ini = now - timedelta(days=7)
        dt_fim = now
    elif periodo == "30d":
        dt_ini = now - timedelta(days=30)
        dt_fim = now
    elif periodo == "3m":
        dt_ini = now - timedelta(days=90)
        dt_fim = now
    elif periodo == "6m":
        dt_ini = now - timedelta(days=180)
        dt_fim = now
    elif periodo == "12m":
        dt_ini = now - timedelta(days=365)
        dt_fim = now
    else:
        # Padrão: últimos 30 dias
        dt_ini = now - timedelta(days=30)
        dt_fim = now

    return dt_ini, dt_fim

async def analyze_period_filtering():
    """Analisa como o filtro de período está afetando os dados"""

    print("🔍 ANALISANDO FILTRO DE PERÍODO")
    print("=" * 80)

    periodo = "30d"
    dt_ini, dt_fim = get_period_filter(periodo)

    print(f"📅 Período analisado: {periodo}")
    print(f"   Data inicial: {dt_ini}")
    print(f"   Data final: {dt_fim}")
    print()

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")

        # Contadores
        total_corridas = 0
        corridas_filtradas = 0
        corridas_por_tipo = {
            "Completed Rides": {"total": 0, "filtradas": 0},
            "Cancelled Rides": {"total": 0, "filtradas": 0},
            "Missed Rides": {"total": 0, "filtradas": 0}
        }

        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name in corridas_por_tipo:
                        tipo = table_name

                        for rec in new_records:
                            total_corridas += 1
                            corridas_por_tipo[tipo]["total"] += 1

                            # Tentar extrair data
                            dt_corrida = None

                            # Índices de data por tipo
                            if "Completed" in tipo:
                                indices_data = [7, 8, 6]
                            elif "Cancelled" in tipo:
                                indices_data = [12, 11, 8, 7]
                            elif "Missed" in tipo:
                                indices_data = [6]
                            else:
                                indices_data = []

                            for idx in indices_data:
                                if idx < len(rec) and rec[idx]:
                                    dt_str = extract_datetime_from_record([rec[idx]], 0)
                                    if dt_str:
                                        try:
                                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                            break
                                        except Exception:
                                            continue

                            # Verificar se passa no filtro
                            if dt_corrida and (dt_ini <= dt_corrida <= dt_fim):
                                corridas_filtradas += 1
                                corridas_por_tipo[tipo]["filtradas"] += 1
                            elif dt_corrida:
                                # Corrida fora do período
                                pass
                            else:
                                # Sem data - pode estar sendo incluída ou não
                                print(f"⚠️  Corrida sem data identificada em {tipo}: {rec[:5]}...")

                except Exception as e:
                    continue

        # Resultados
        print("\n📈 RESULTADOS DA FILTRAGEM:")
        print("-" * 50)
        print(f"Total de corridas no banco: {total_corridas}")
        print(f"Corridas no período {periodo}: {corridas_filtradas}")
        print(f"Percentual filtrado: {(corridas_filtradas / total_corridas * 100):.1f}%")
        print("\n📊 POR TIPO:")
        for tipo, counts in corridas_por_tipo.items():
            percentual = (counts["filtradas"] / counts["total"] * 100) if counts["total"] > 0 else 0
            print(f"{tipo}:")
            print(f"  Total: {counts['total']}")
            print(f"  Filtradas: {counts['filtradas']} ({percentual:.1f}%)")

        print("\n🎯 COMPARAÇÃO COM OS KPIs:")
        print("-" * 50)
        print("KPIs esperados (30d):")
        print("  Concluídas: ~146")
        print("  Canceladas: ~15")
        print("  Perdidas: ~90")
        print("  Total: ~251")
        print()
        print("Mapa atual:")
        print(f"  Concluídas: {corridas_por_tipo['Completed Rides']['filtradas']}")
        print(f"  Canceladas: {corridas_por_tipo['Cancelled Rides']['filtradas']}")
        print(f"  Perdidas: {corridas_por_tipo['Missed Rides']['filtradas']}")
        print(f"  Total: {corridas_filtradas}")

if __name__ == "__main__":
    import re
    asyncio.run(analyze_period_filtering())