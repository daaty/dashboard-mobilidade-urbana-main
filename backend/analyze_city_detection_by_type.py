import asyncio
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from services.city_service import normalize_city_name, extract_city_from_address

def extract_city_from_record_debug(rec, table_name):
    """Versão debug da função extract_city_from_record"""
    print(f"\n=== Analisando registro de {table_name} ===")
    print(f"Comprimento do registro: {len(rec)}")
    print(f"Registro completo: {rec}")

    # Priorizar índices onde as cidades realmente aparecem nos dados atuais
    possible_city_indices = [5, 6, 15, 17, 8, 9, 10]  # Reordenado por prioridade baseada nos dados

    for idx in possible_city_indices:
        if idx < len(rec) and rec[idx]:
            city_str = str(rec[idx]).strip()
            print(f"Índice {idx}: '{city_str}'")

            # Primeiro tentar normalização direta
            normalized_city = normalize_city_name(city_str)
            if normalized_city:
                print(f"  -> Cidade normalizada: {normalized_city}")
                return normalized_city

            # Se não conseguiu normalizar diretamente, tentar extrair de endereço
            extracted_city = extract_city_from_address(city_str)
            if extracted_city:
                print(f"  -> Cidade extraída de endereço: {extracted_city}")
                return extracted_city

    print("  -> Nenhuma cidade detectada")
    return "Unnamed"

async def analyze_city_detection():
    """Analisa como as cidades são detectadas para diferentes tipos de corridas"""
    async with SessionLocal() as session:
        # Buscar dados de diferentes tipos de corridas
        tables_to_analyze = [
            ("Completed Rides", "concluidas"),
            ("Cancelled Rides", "canceladas"),
            ("Missed Rides", "perdidas")
        ]

        for table_name, tipo in tables_to_analyze:
            print(f"\n{'='*60}")
            print(f"ANALISANDO {table_name.upper()} ({tipo})")
            print(f"{'='*60}")

            # Buscar alguns registros de exemplo
            query = select(RidesData).where(RidesData.table_name == table_name).limit(5)
            result = await session.execute(query)
            records = result.scalars().all()

            print(f"Encontrados {len(records)} registros de exemplo")

            for i, record in enumerate(records):
                print(f"\n--- Registro {i+1} ---")
                rec_data = json.loads(record.ride_data) if isinstance(record.ride_data, str) else record.ride_data
                detected_city = extract_city_from_record_debug(rec_data, table_name)

                print(f"Cidade detectada final: {detected_city}")

if __name__ == "__main__":
    # Adicionar caminho do projeto
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    import json
    asyncio.run(analyze_city_detection())