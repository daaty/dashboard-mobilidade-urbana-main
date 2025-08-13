#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

# Testar importações
try:
    print("Testando importações...")
    from fastapi import FastAPI
    print("✅ FastAPI importado")
    
    from app.database import get_db
    print("✅ Database importado")
    
    from app.models.rides_data import RidesData
    print("✅ Model importado")
    
    import json
    from datetime import datetime, timedelta
    print("✅ JSON e datetime importados")
    
    print("\n🔍 Testando conexão com banco...")
    
    # Testar conexão com banco
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from dotenv import load_dotenv
    
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        rides = session.query(RidesData).all()
        print(f"✅ Conectado ao banco - {len(rides)} registros")
        
        # Testar processamento básico
        print("\n🔍 Testando processamento básico...")
        
        now = datetime.now()
        dt_ini = now - timedelta(days=150)
        dt_fim = now
        
        concluidas = []
        canceladas = []
        
        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                ride_data = json.loads(ride_data)
            
            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])
            
            if table_name == "Completed Rides":
                print(f"  📊 Processando {len(new_records)} corridas concluídas...")
                for rec in new_records:
                    try:
                        if len(rec) > 6:
                            hora = rec[6]
                            if hora and "2025" in str(hora):
                                dt_corrida = datetime.strptime(hora, "%Y-%m-%d %H:%M:%S")
                                if dt_ini <= dt_corrida <= dt_fim:
                                    concluidas.append({
                                        "id": rec[0],
                                        "nome": rec[2] or rec[1] or "Usuário",
                                        "hora": hora
                                    })
                    except Exception as e:
                        print(f"    ❌ Erro no registro: {e}")
                        
            elif table_name == "Cancelled Rides":
                print(f"  📊 Processando {len(new_records)} corridas canceladas...")
                for rec in new_records:
                    try:
                        if len(rec) > 11:
                            hora = rec[11]
                            if hora and "2025" in str(hora):
                                dt_corrida = datetime.strptime(hora, "%Y-%m-%d %H:%M:%S")
                                if dt_ini <= dt_corrida <= dt_fim:
                                    canceladas.append({
                                        "id": rec[0],
                                        "nome": rec[2] or "Usuário",
                                        "hora": hora
                                    })
                    except Exception as e:
                        print(f"    ❌ Erro no registro: {e}")
        
        print(f"\n📊 RESULTADO:")
        print(f"  ✅ Concluídas: {len(concluidas)}")
        print(f"  ❌ Canceladas: {len(canceladas)}")
        
        # Testar criação de resposta básica
        response = {
            "metricas_principais": {
                "corridas_concluidas": len(concluidas),
                "corridas_canceladas": len(canceladas),
                "corridas_perdidas": 0
            },
            "atividade_recente": {
                "concluidas": concluidas[:5],
                "canceladas": canceladas[:5],
                "perdidas": []
            }
        }
        
        print(f"\n📋 Resposta criada: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
    print("\n✅ Todos os testes passaram!")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
