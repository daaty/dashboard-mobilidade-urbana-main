import sys
import os
import asyncio
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy import select

async def find_correct_location_indices():
    """Encontra os índices corretos para endereços/bairros nos dados das corridas"""

    print("🔍 BUSCANDO ÍNDICES CORRETOS PARA ENDEREÇOS/BAIRROS")
    print("=" * 80)

    async with SessionLocal() as session:
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()

        print(f"📊 Analisando {len(rides)} registros...")
        print()

        # Analisar diferentes tipos
        location_examples = {
            "Completed Rides": [],
            "Cancelled Rides": [],
            "Missed Rides": []
        }

        for r in rides:
            if r.ride_data:
                try:
                    ride_data = json.loads(r.ride_data) if isinstance(r.ride_data, str) else r.ride_data
                    table_name = ride_data.get("tableName", "")
                    new_records = ride_data.get("newRecords", [])

                    if table_name in location_examples and len(location_examples[table_name]) < 5:
                        if new_records and len(new_records) > 0:
                            # Pegar primeiro record e procurar por campos que parecem endereços
                            record = new_records[0]
                            enderecos_potential = []

                            for idx, campo in enumerate(record):
                                campo_str = str(campo).lower().strip()
                                # Procurar por padrões de endereço
                                if any(keyword in campo_str for keyword in [
                                    'rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça',
                                    'bairro', 'centro', 'vila', 'jardim', 'parque',
                                    'setor', 'loteamento', 'condomínio', 'residencial',
                                    'estrada', 'rodovia', 'km', 'número', 'n°', 'nº'
                                ]) and len(campo_str) > 10 and campo_str != 'nan':
                                    enderecos_potential.append({
                                        'indice': idx,
                                        'valor': campo,
                                        'tipo': 'POTENCIAL_ENDERECO'
                                    })

                            if enderecos_potential:
                                location_examples[table_name].append({
                                    'registro_id': r.id,
                                    'record': record,
                                    'enderecos_encontrados': enderecos_potential
                                })

                except Exception as e:
                    continue

        # Mostrar resultados
        for tipo, exemplos in location_examples.items():
            print(f"\n🎯 {tipo.upper()}")
            print("-" * 50)

            if not exemplos:
                print("❌ Nenhum endereço potencial encontrado")
                continue

            for i, exemplo in enumerate(exemplos[:3]):  # Mostrar até 3 exemplos
                print(f"\n📋 Exemplo {i+1} (Registro ID: {exemplo['registro_id']})")
                print("   Endereços encontrados:")
                for endereco in exemplo['enderecos_encontrados']:
                    print(f"      [{endereco['indice']}]: {endereco['valor'][:80]}...")

                # Mostrar estrutura completa do record para análise
                print("\n   📊 Estrutura completa do record:")
                record = exemplo['record']
                for idx, campo in enumerate(record):
                    marker = " ← ENDEREÇO?" if any(e['indice'] == idx for e in exemplo['enderecos_encontrados']) else ""
                    print(f"      [{idx}]: {str(campo)[:60]}{marker}")

        print("\n" + "=" * 80)
        print("🔧 RECOMENDAÇÕES PARA CORREÇÃO:")
        print()
        print("Baseado na análise, os índices corretos devem ser:")
        print()
        print("🔸 Completed Rides:")
        print("   - Procurar por campos com 'rua', 'avenida', 'bairro', etc.")
        print("   - Evitar índices [4] que estão pegando telefones")
        print()
        print("🔸 Cancelled Rides:")
        print("   - Mesmo problema - índices incorretos")
        print("   - Procurar por endereços em índices mais altos")
        print()
        print("🔸 Missed Rides:")
        print("   - Índice [3] parece estar correto")
        print()
        print("💡 PRÓXIMOS PASSOS:")
        print("   1. Atualizar os índices no endpoint /mapa-calor-problemas")
        print("   2. Adicionar validação para verificar se o campo é realmente um endereço")
        print("   3. Implementar geocodificação apenas para campos que contenham endereços válidos")

if __name__ == "__main__":
    asyncio.run(find_correct_location_indices())