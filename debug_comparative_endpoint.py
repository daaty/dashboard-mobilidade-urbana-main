#!/usr/bin/env python3
import psycopg2
import json
from datetime import datetime
import re

def extract_datetime_from_record(record, index):
    """Extrai data/hora de um registro usando regex"""
    if not record or index >= len(record):
        return None
    
    value = str(record[index])
    
    # Padrões de regex para diferentes formatos
    patterns = [
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # YYYY-MM-DD HH:MM:SS
        r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',  # DD/MM/YYYY HH:MM:SS
        r'(\d{4}-\d{2}-\d{2})',                    # YYYY-MM-DD
        r'(\d{2}/\d{2}/\d{4})',                    # DD/MM/YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)
    
    return None

def debug_endpoint_logic():
    """Debug da lógica do endpoint comparative"""
    
    # Conectar ao banco (usando dados do .env)
    conn = psycopg2.connect(
        host="148.230.73.27",
        port=5432,
        database="n8n_db",
        user="n8n_user",
        password="n8n_pw"
    )
    cur = conn.cursor()
    
    # Buscar dados
    cur.execute("SELECT * FROM rides_data ORDER BY id")
    rows = cur.fetchall()
    
    # Analisar setembro especificamente
    print("🔍 ANÁLISE DETALHADA - SETEMBRO 2025")
    print("=" * 60)
    
    corridas_setembro = {
        "concluidas": 0,
        "canceladas": 0,
        "perdidas": 0,
        "por_dia": {}
    }
    
    # Inicializar contadores por dia
    for dia in range(1, 32):
        corridas_setembro["por_dia"][dia] = {
            "concluidas": 0,
            "canceladas": 0,
            "perdidas": 0,
            "total": 0
        }
    
    total_registros_processados = 0
    registros_setembro = 0
    
    for row in rows:
        table_id, table_name, data_hash, ride_data_str, scraped_at, session_info, source = row
        
        try:
            ride_data = json.loads(ride_data_str)
        except:
            continue
            
        table_name = ride_data.get("tableName", "")
        new_records = ride_data.get("newRecords", [])
        
        total_registros_processados += len(new_records)
        
        print(f"\n📋 Tabela: {table_name}")
        print(f"   Fonte: {source}")
        print(f"   Registros: {len(new_records)}")
        
        # Processar corridas concluídas
        if table_name in ["Completed Rides", "corridas_concluidas", "rides_data"]:
            print(f"   🟢 Processando CONCLUÍDAS...")
            for i, rec in enumerate(new_records):
                # Extrair data e status baseado na fonte
                if source == "import_excel":
                    hora = rec[6] if len(rec) > 6 else None
                    status = rec[9] if len(rec) > 9 else None
                else:
                    hora = rec[7] if len(rec) > 7 else None
                    status = rec[10] if len(rec) > 10 else None
                
                # Verificar se é realmente concluída
                if status and "Concluído" not in str(status) and "Completed" not in str(status):
                    continue
                
                # Extrair data
                if hora:
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            if dt_corrida.year == 2025 and dt_corrida.month == 9:
                                registros_setembro += 1
                                dia_corrida = dt_corrida.day
                                corridas_setembro["concluidas"] += 1
                                corridas_setembro["por_dia"][dia_corrida]["concluidas"] += 1
                                
                                if i < 3:  # Mostrar primeiros 3 registros como exemplo
                                    print(f"     ✅ Dia {dia_corrida}: {dt_str} - Status: {status}")
                        except Exception as e:
                            print(f"     ❌ Erro ao processar data: {hora} - {e}")
        
        # Processar corridas canceladas 
        elif table_name in ["Cancelled Rides", "corridas_canceladas"]:
            print(f"   🟡 Processando CANCELADAS...")
            for i, rec in enumerate(new_records):
                # Extrair data e status baseado na fonte
                if source == "import_excel":
                    hora = rec[11] if len(rec) > 11 else None
                    status = rec[13] if len(rec) > 13 else None
                else:
                    hora = rec[12] if len(rec) > 12 else None
                    status = rec[14] if len(rec) > 14 else None
                
                # Verificar se é realmente cancelada
                if status and "Cancel" not in str(status) and "cancel" not in str(status):
                    continue
                
                # Extrair data
                if hora:
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            if dt_corrida.year == 2025 and dt_corrida.month == 9:
                                registros_setembro += 1
                                dia_corrida = dt_corrida.day
                                corridas_setembro["canceladas"] += 1
                                corridas_setembro["por_dia"][dia_corrida]["canceladas"] += 1
                                
                                if i < 3:
                                    print(f"     🟡 Dia {dia_corrida}: {dt_str} - Status: {status}")
                        except Exception as e:
                            print(f"     ❌ Erro ao processar data: {hora} - {e}")
        
        # Processar corridas perdidas
        elif table_name in ["Missed Rides", "corridas_perdidas", "Scheduled Rides", "corridas_agendadas"]:
            print(f"   🔴 Processando PERDIDAS/MISSED...")
            for i, rec in enumerate(new_records):
                # Extrair data e status baseado na fonte
                if source == "import_excel":
                    hora = rec[6] if len(rec) > 6 else None
                    status = rec[5] if len(rec) > 5 else None
                else:
                    if table_name in ["Scheduled Rides", "corridas_agendadas"]:
                        hora = rec[10] if len(rec) > 10 else None
                        status = rec[14] if len(rec) > 14 else None
                    else:
                        hora = rec[6] if len(rec) > 6 else None
                        status = rec[5] if len(rec) > 5 else None
                
                # Verificar se é realmente perdida/missed/timeout
                if status and not any(word in str(status) for word in ["Timeout", "Missed", "Process", "perdida"]):
                    continue
                
                # Extrair data
                if hora:
                    dt_str = extract_datetime_from_record([hora], 0)
                    if dt_str:
                        try:
                            dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            if dt_corrida.year == 2025 and dt_corrida.month == 9:
                                registros_setembro += 1
                                dia_corrida = dt_corrida.day
                                corridas_setembro["perdidas"] += 1
                                corridas_setembro["por_dia"][dia_corrida]["perdidas"] += 1
                                
                                if i < 3:
                                    print(f"     🔴 Dia {dia_corrida}: {dt_str} - Status: {status}")
                        except Exception as e:
                            print(f"     ❌ Erro ao processar data: {hora} - {e}")
    
    # Calcular total por dia
    for dia in range(1, 32):
        corridas_setembro["por_dia"][dia]["total"] = (
            corridas_setembro["por_dia"][dia]["concluidas"] + 
            corridas_setembro["por_dia"][dia]["canceladas"] + 
            corridas_setembro["por_dia"][dia]["perdidas"]
        )
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO SETEMBRO 2025:")
    print(f"   ✅ Concluídas: {corridas_setembro['concluidas']}")
    print(f"   🟡 Canceladas: {corridas_setembro['canceladas']}")
    print(f"   🔴 Perdidas: {corridas_setembro['perdidas']}")
    print(f"   📈 TOTAL SETEMBRO: {corridas_setembro['concluidas'] + corridas_setembro['canceladas'] + corridas_setembro['perdidas']}")
    
    print(f"\n📋 Registros processados total: {total_registros_processados}")
    print(f"📋 Registros de setembro: {registros_setembro}")
    
    # Mostrar dias com mais corridas
    print(f"\n🎯 DIAS COM MAIS CORRIDAS EM SETEMBRO:")
    dias_ordenados = sorted(corridas_setembro["por_dia"].items(), 
                          key=lambda x: x[1]["total"], reverse=True)
    
    for dia, dados in dias_ordenados[:10]:  # Top 10 dias
        if dados["total"] > 0:
            print(f"   Dia {dia:2d}: {dados['total']:3d} corridas "
                  f"(✅{dados['concluidas']} 🟡{dados['canceladas']} 🔴{dados['perdidas']})")
    
    # Verificar especificamente o dia 13
    dia13 = corridas_setembro["por_dia"][13]
    print(f"\n🔍 DIA 13 DE SETEMBRO (REPORTADO COMO PROBLEMA):")
    print(f"   ✅ Concluídas: {dia13['concluidas']}")
    print(f"   🟡 Canceladas: {dia13['canceladas']}")
    print(f"   🔴 Perdidas: {dia13['perdidas']}")
    print(f"   📈 TOTAL DIA 13: {dia13['total']}")
    
    conn.close()

if __name__ == "__main__":
    debug_endpoint_logic()