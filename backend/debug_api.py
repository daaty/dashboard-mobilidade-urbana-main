#!/usr/bin/env python3
import sys
import os
sys.path.append('.')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.rides_data import RidesData
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def debug_api_processing():
    # Usar a string de conexão PostgreSQL correta
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        rides = session.query(RidesData).all()
        print(f"🔍 Total de registros: {len(rides)}")
        
        # Configurar datas como na API
        now = datetime.now()
        dt_ini = now - timedelta(days=150)  # Mesmo período da API
        dt_fim = now
        
        print(f"📅 Período: {dt_ini} até {dt_fim}")
        
        concluidas = []
        canceladas = []
        
        try:
            for r in rides:
                print(f"\n📋 Processando registro: {r.table_name}")
                
                ride_data = r.ride_data
                if isinstance(ride_data, str):
                    try:
                        ride_data = json.loads(ride_data)
                    except Exception as e:
                        print(f"❌ Erro JSON: {e}")
                        continue
                        
                table_name = ride_data.get("tableName", "")
                new_records = ride_data.get("newRecords", [])
                
                print(f"  🏷️ Table name: {table_name}")
                print(f"  📊 Records: {len(new_records)}")
                
                # Testar processamento de Completed Rides
                if table_name in ["Completed Rides", "corridas_concluidas"]:
                    print("  ✅ Processando corridas concluídas...")
                    
                    for i, rec in enumerate(new_records[:2]):  # Só 2 para debug
                        try:
                            print(f"\n    🔍 Registro {i+1}:")
                            print(f"      📋 Tamanho: {len(rec)}")
                            
                            id_corrida = rec[0] if len(rec) > 0 else None
                            nome_motorista = rec[1] if len(rec) > 1 else None
                            nome_passageiro = rec[2] if len(rec) > 2 else None
                            telefone = rec[3] if len(rec) > 3 else None
                            
                            nome = nome_passageiro or nome_motorista or "Usuário"
                            hora = rec[6] if len(rec) > 6 else None
                            
                            print(f"      🆔 ID: {id_corrida}")
                            print(f"      👤 Nome: {nome}")
                            print(f"      📅 Hora raw: {hora}")
                            
                            dt_corrida = None
                            hora_formatada = None
                            
                            if hora:
                                import re
                                match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", hora)
                                if match:
                                    dt_str = match.group(1)
                                    try:
                                        dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                        hora_formatada = dt_str
                                        print(f"      ✅ Data parseada: {dt_corrida}")
                                    except Exception as e:
                                        print(f"      ❌ Erro parse data: {e}")
                                        dt_corrida = None
                                        hora_formatada = None
                                else:
                                    print(f"      ❌ Regex não encontrou data em: {hora}")
                                    hora_formatada = hora
                            
                            # Verificar se está no período
                            if dt_corrida:
                                if dt_ini <= dt_corrida <= dt_fim:
                                    print(f"      ✅ Data no período válido")
                                    concluidas.append({
                                        "id_corrida": id_corrida,
                                        "nome": nome,
                                        "hora": hora_formatada
                                    })
                                else:
                                    print(f"      ❌ Data fora do período")
                            else:
                                print(f"      ❌ Data inválida")
                                
                        except Exception as e:
                            print(f"      ❌ Erro ao processar registro: {e}")
                            import traceback
                            traceback.print_exc()
                
                # Testar processamento de Cancelled Rides  
                elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
                    print("  ✅ Processando corridas canceladas...")
                    
                    for i, rec in enumerate(new_records[:2]):  # Só 2 para debug
                        try:
                            print(f"\n    🔍 Registro {i+1}:")
                            
                            id_corrida = rec[0] if len(rec) > 0 else None
                            nome = rec[2] if len(rec) > 2 else None
                            hora = rec[11] if len(rec) > 11 else None
                            
                            print(f"      🆔 ID: {id_corrida}")
                            print(f"      👤 Nome: {nome}")
                            print(f"      📅 Hora raw: {hora}")
                            
                            dt_corrida = None
                            if hora:
                                import re
                                match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", hora)
                                if match:
                                    dt_str = match.group(1)
                                    try:
                                        dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                        print(f"      ✅ Data parseada: {dt_corrida}")
                                    except Exception as e:
                                        print(f"      ❌ Erro parse data: {e}")
                            
                            if dt_corrida and dt_ini <= dt_corrida <= dt_fim:
                                print(f"      ✅ Data no período válido")
                                canceladas.append({
                                    "id_corrida": id_corrida,
                                    "nome": nome,
                                    "hora": dt_str
                                })
                                
                        except Exception as e:
                            print(f"      ❌ Erro ao processar cancelada: {e}")
                            import traceback
                            traceback.print_exc()
        
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n📊 RESULTADOS:")
        print(f"  ✅ Concluídas: {len(concluidas)}")
        print(f"  ❌ Canceladas: {len(canceladas)}")
        
        if concluidas:
            print(f"\n  Exemplo concluída: {concluidas[0]}")
        if canceladas:
            print(f"  Exemplo cancelada: {canceladas[0]}")

if __name__ == "__main__":
    debug_api_processing()
