import asyncio
from sqlalchemy import select
from backend.app.database import get_db
from backend.app.models.rides_data import RidesData
import json

async def debug_duplicate_records():
    """Analisar se há registros duplicados que causam contagem excessiva"""
    print("🔍 DEBUGANDO REGISTROS DUPLICADOS...")
    print("="*50)
    
    # Conectar ao banco
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        # Buscar todos os registros
        result = await db.execute(select(RidesData))
        rides = result.scalars().all()
        
        print(f"📊 TOTAL DE REGISTROS: {len(rides)}")
        
        # Analisar registros de setembro especificamente
        setembro_records = []
        data_contador = {}
        
        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except:
                    continue
                    
            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])
            source = r.source
            
            # Focar em registros que podem ser de setembro
            if table_name in ["Completed Rides", "corridas_concluidas", "rides_data"]:
                for rec in new_records:
                    # Extrair data do registro
                    if source == "import_excel":
                        hora = rec[6] if len(rec) > 6 else None
                    else:
                        hora = rec[7] if len(rec) > 7 else None
                        
                    if hora and "202509" in str(hora):  # Setembro 2025
                        data_key = str(hora)[:8]  # YYYYMMDD
                        if data_key not in data_contador:
                            data_contador[data_key] = 0
                        data_contador[data_key] += 1
                        
                        setembro_records.append({
                            'data': data_key,
                            'source': source,
                            'table': table_name,
                            'hora_raw': hora,
                            'record_id': r.id
                        })
        
        # Mostrar contadores por dia
        print(f"\n📅 CONTAGEM POR DIA EM SETEMBRO:")
        for data in sorted(data_contador.keys()):
            if data.startswith('20250908'):  # Dia 8 especificamente
                count = data_contador[data]
                print(f"  📍 DIA 8 (20250908): {count} registros encontrados")
                
                # Mostrar detalhes dos registros do dia 8
                print("     DETALHES DOS REGISTROS:")
                dia_8_records = [r for r in setembro_records if r['data'].startswith('20250908')]
                
                sources = {}
                for rec in dia_8_records:
                    source = rec['source']
                    if source not in sources:
                        sources[source] = []
                    sources[source].append(rec)
                
                for source, recs in sources.items():
                    print(f"       {source}: {len(recs)} registros")
                    for rec in recs[:5]:  # Mostrar primeiros 5
                        print(f"         - Record ID {rec['record_id']}: {rec['hora_raw']}")
                
                # Verificar duplicatas exatas
                horas_unicas = set()
                duplicatas = 0
                for rec in dia_8_records:
                    hora = rec['hora_raw']
                    if hora in horas_unicas:
                        duplicatas += 1
                    else:
                        horas_unicas.add(hora)
                
                print(f"       🚨 DUPLICATAS EXATAS: {duplicatas}")
                print(f"       ✅ REGISTROS ÚNICOS: {len(horas_unicas)}")
                
                if duplicatas > 0:
                    print("       ⚠️ PROBLEMA: Há registros duplicados!")
                else:
                    print("       ℹ️ INFO: Não há duplicatas exatas, pode ser agrupamento incorreto")
                    
                break
        
    finally:
        await db.close()

# Executar debug
if __name__ == "__main__":
    asyncio.run(debug_duplicate_records())