#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
import json
import re
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.rides_data import RidesData
from dotenv import load_dotenv

load_dotenv()

def main():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    # Converter para psycopg2 para conexão síncrona
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        rides = session.query(RidesData).filter_by(table_name="Cancelled Rides").all()
        print(f'🔍 Total de registros Cancelled Rides: {len(rides)}')
        
        if len(rides) == 0:
            print("❌ Nenhuma corrida cancelada encontrada")
            return
            
        # Definir período de 30 dias
        now = datetime.now()
        dt_ini = now - timedelta(days=30)
        dt_fim = now
        
        print(f"📅 Período de análise: {dt_ini.strftime('%Y-%m-%d %H:%M:%S')} até {dt_fim.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for ride in rides:
            if not ride.ride_data:
                print("❌ ride_data vazio")
                continue
                
            try:
                ride_data = json.loads(ride.ride_data) if isinstance(ride.ride_data, str) else ride.ride_data
                table_name = ride_data.get("tableName", "")
                new_records = ride_data.get("newRecords", [])
                
                print(f"\n📋 Registro ride_data:")
                print(f"  🏷️ tableName: {table_name}")
                print(f"  📊 newRecords count: {len(new_records)}")
                
                if table_name == "Cancelled Rides":
                    print("\n🔍 Analisando registros cancelados:")
                    
                    for i, rec in enumerate(new_records[:3]):  # Mostrar apenas os primeiros 3
                        print(f"\n  📝 Registro {i+1}: {rec}")
                        
                        id_corrida = rec[0] if len(rec) > 0 else None
                        nome = rec[2] if len(rec) > 2 else None
                        hora = rec[9] if len(rec) > 9 else None
                        motivo = rec[10] if len(rec) > 10 else None
                        
                        print(f"    🆔 ID: {id_corrida}")
                        print(f"    👤 Nome: {nome}")
                        print(f"    🕐 Hora raw: {hora}")
                        print(f"    ❌ Motivo: {motivo}")
                        
                        # Tentar extrair data
                        dt_corrida = None
                        hora_formatada = None
                        if hora:
                            match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", str(hora))
                            if match:
                                dt_str = match.group(1)
                                try:
                                    dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                    hora_formatada = dt_str
                                    print(f"    ✅ Data parseada: {dt_corrida}")
                                    
                                    # Verificar se está no período
                                    if dt_ini <= dt_corrida <= dt_fim:
                                        print(f"    ✅ DENTRO do período de 30 dias")
                                    else:
                                        print(f"    ❌ FORA do período de 30 dias")
                                        print(f"       Diferença: {(now - dt_corrida).days} dias atrás")
                                except Exception as e:
                                    print(f"    ❌ Erro ao parsear data: {e}")
                            else:
                                print(f"    ❌ Regex não encontrou data no formato esperado")
                        else:
                            print(f"    ❌ Campo hora está vazio")
                            
            except Exception as e:
                print(f"❌ Erro ao processar ride_data: {e}")

if __name__ == "__main__":
    main()
