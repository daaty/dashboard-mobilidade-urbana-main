import sys
import os
import asyncio
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select

async def analyze_ride_structure():
    """Analisa a estrutura dos dados das corridas para verificar índices do mapa de calor"""

    print("🔍 ANÁLISE DA ESTRUTURA DOS DADOS DAS CORRIDAS")
    print("=" * 80)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Total de registros na tabela: {len(rides)}")
        print()

        # Analisar diferentes tipos de corridas
        tipos_analisados = {
            "Completed Rides": [],
            "Cancelled Rides": [],
            "Missed Rides": []
        }

        for i, r in enumerate(rides):
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name in tipos_analisados and len(tipos_analisados[table_name]) < 3:
                        # Guardar até 3 exemplos de cada tipo
                        if new_records and len(new_records) > 0:
                            tipos_analisados[table_name].append({
                                'registro_id': r.id,
                                'table_name': table_name,
                                'primeiro_record': new_records[0],
                                'total_records': len(new_records)
                            })

                except Exception as e:
                    continue

        # Mostrar análise por tipo
        for tipo, exemplos in tipos_analisados.items():
            print(f"\n🎯 ANÁLISE: {tipo.upper()}")
            print("-" * 50)

            if not exemplos:
                print("❌ Nenhum exemplo encontrado")
                continue

            for i, exemplo in enumerate(exemplos):
                print(f"\n📋 Exemplo {i+1} (Registro ID: {exemplo['registro_id']})")
                print(f"   Total de records: {exemplo['total_records']}")
                print(f"   Primeiro record (estrutura completa):")
                record = exemplo['primeiro_record']

                # Mostrar estrutura do record
                print(f"   📊 Record tem {len(record)} campos:")
                for idx, campo in enumerate(record):
                    print(f"      [{idx}]: {campo} ({type(campo).__name__})")

                print("\n   🔍 ANÁLISE DOS ÍNDICES USADOS NO MAPA DE CALOR:")

                if tipo == "Completed Rides":
                    print("      ✅ Bairro esperado no índice [4]:", record[4] if len(record) > 4 else "❌ ÍNDICE FORA DOS LIMITES")
                    if len(record) > 4:
                        print(f"         Tipo do campo: {type(record[4]).__name__}")

                elif tipo == "Cancelled Rides":
                    indices_canceladas = [4, 5, 6, 7, 8]
                    for idx in indices_canceladas:
                        campo = record[idx] if len(record) > idx else "❌ ÍNDICE FORA DOS LIMITES"
                        print(f"      [{idx}]: {campo}")
                        if idx == 4: print("         ↳ ENDEREÇO (esperado)")
                        elif idx == 5: print("         ↳ BAIRRO (esperado)")
                        elif idx == 6: print("         ↳ MOTIVO (esperado)")
                        elif idx == 7: print("         ↳ CIDADE (esperado)")
                        elif idx == 8: print("         ↳ ESTADO (esperado)")

                elif tipo == "Missed Rides":
                    indices_perdidas = [3, 5, 6]
                    for idx in indices_perdidas:
                        campo = record[idx] if len(record) > idx else "❌ ÍNDICE FORA DOS LIMITES"
                        print(f"      [{idx}]: {campo}")
                        if idx == 3: print("         ↳ BAIRRO (esperado)")
                        elif idx == 5: print("         ↳ MOTIVO (esperado)")
                        elif idx == 6: print("         ↳ DATA (esperado)")

                print()

        print("\n" + "=" * 80)
        print("📋 RESUMO DOS ÍNDICES USADOS NO MAPA DE CALOR:")
        print()
        print("🔸 Completed Rides:")
        print("   - Bairro: índice [4]")
        print()
        print("🔸 Cancelled Rides:")
        print("   - Endereço: índice [4]")
        print("   - Bairro: índice [5]")
        print("   - Motivo: índice [6]")
        print("   - Cidade: índice [7]")
        print("   - Estado: índice [8]")
        print()
        print("🔸 Missed Rides:")
        print("   - Bairro: índice [3]")
        print("   - Motivo: índice [5]")
        print("   - Data: índice [6]")
        print()
        print("⚠️  IMPORTANTE: Verificar se todos os registros têm pelo menos")
        print("   o número mínimo de campos esperado para cada tipo!")

if __name__ == "__main__":
    asyncio.run(analyze_ride_structure())