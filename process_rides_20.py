#!/usr/bin/env python3
"""
Script para processar e analisar as corridas do dia 20 encontradas
"""
import psycopg2
import json
from datetime import datetime

def process_rides_day_20():
    DATABASE_URL = 'postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db'
    print(f'🔍 PROCESSANDO CORRIDAS DO DIA 20/08/2025 ENCONTRADAS NA VPS')
    print("="*80)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Pegar especificamente o registro ID 16 que contém as corridas do dia 20
        cursor.execute("""
            SELECT 
                id,
                table_name,
                ride_data,
                scraped_at,
                session_info,
                source
            FROM rides_data 
            WHERE id = 16;
        """)
        registro = cursor.fetchone()
        
        if registro:
            id_reg = registro[0]
            table_name = registro[1]
            ride_data_str = registro[2]
            scraped_at = registro[3]
            session_info = registro[4]
            source = registro[5]
            
            print(f"📋 Analisando registro ID: {id_reg}")
            print(f"🏷️  Table Name: {table_name}")
            print(f"🕐 Scraped At: {scraped_at}")
            print(f"📡 Source: {source}")
            
            if ride_data_str:
                ride_data = json.loads(ride_data_str)
                
                print(f"\n🎯 DADOS DAS CORRIDAS DO DIA 20:")
                print("="*80)
                
                if 'newRecords' in ride_data and isinstance(ride_data['newRecords'], list):
                    corridas_dia_20 = []
                    
                    for record in ride_data['newRecords']:
                        if isinstance(record, list) and len(record) > 7:
                            # Analisar estrutura do registro
                            # Com base na estrutura observada:
                            # [0] = id_corrida, [2] = nome_motorista, [3] = nome_passageiro
                            # [4] = telefone, [5] = origem, [6] = destino
                            # [7] = data_solicitacao, [8] = data_conclusao, [9] = categoria
                            # [10] = status, etc.
                            
                            try:
                                id_corrida = record[0]
                                nome_motorista = record[2] if len(record) > 2 else "N/A"
                                nome_passageiro = record[3] if len(record) > 3 else "N/A"
                                telefone = record[4] if len(record) > 4 else "N/A"
                                origem = record[5] if len(record) > 5 else "N/A"
                                destino = record[6] if len(record) > 6 else "N/A"
                                data_solicitacao = record[7] if len(record) > 7 else "N/A"
                                data_conclusao = record[8] if len(record) > 8 else "N/A"
                                categoria = record[9] if len(record) > 9 else "N/A"
                                status = record[10] if len(record) > 10 else "N/A"
                                
                                # Verificar se contém data do dia 20
                                data_str = str(data_solicitacao) + str(data_conclusao)
                                if '2025-08-20' in data_str:
                                    corrida_info = {
                                        'id_corrida': id_corrida,
                                        'nome_motorista': nome_motorista,
                                        'nome_passageiro': nome_passageiro,
                                        'telefone': telefone,
                                        'origem': origem,
                                        'destino': destino,
                                        'data_solicitacao': data_solicitacao,
                                        'data_conclusao': data_conclusao,
                                        'categoria': categoria,
                                        'status': status,
                                        'registro_completo': record
                                    }
                                    corridas_dia_20.append(corrida_info)
                                    
                            except Exception as e:
                                print(f"⚠️  Erro ao processar registro: {e}")
                    
                    if corridas_dia_20:
                        print(f"✅ ENCONTRADAS {len(corridas_dia_20)} CORRIDAS DO DIA 20/08/2025!")
                        print("="*80)
                        
                        for idx, corrida in enumerate(corridas_dia_20, 1):
                            print(f"\n🚗 CORRIDA {idx}:")
                            print(f"   📊 ID: {corrida['id_corrida']}")
                            print(f"   🚘 Motorista: {corrida['nome_motorista']}")
                            print(f"   👤 Passageiro: {corrida['nome_passageiro']}")
                            print(f"   📱 Telefone: {corrida['telefone']}")
                            print(f"   📍 Origem: {corrida['origem'][:80]}...")
                            print(f"   🎯 Destino: {corrida['destino'][:80]}...")
                            print(f"   🕐 Solicitação: {corrida['data_solicitacao']}")
                            print(f"   ✅ Conclusão: {corrida['data_conclusao']}")
                            print(f"   🏷️  Categoria: {corrida['categoria']}")
                            print(f"   📊 Status: {corrida['status']}")
                            print(f"   📋 Registro completo: {corrida['registro_completo']}")
                            print("-" * 60)
                        
                        # Analisar horários
                        print(f"\n📊 ANÁLISE DOS HORÁRIOS:")
                        horarios = []
                        for corrida in corridas_dia_20:
                            try:
                                # Extrair horário da data de solicitação
                                data_str = str(corrida['data_solicitacao'])
                                if '2025-08-20' in data_str:
                                    # Formato parece ser "202508202025-08-20 HH:MM:SS"
                                    if ' ' in data_str:
                                        hora_part = data_str.split(' ')[-1]  # Pegar a parte após o espaço
                                        if ':' in hora_part:
                                            hora = hora_part.split(':')[0]
                                            horarios.append(f"{hora}h")
                            except:
                                pass
                        
                        if horarios:
                            print(f"   🕐 Horários das corridas: {', '.join(horarios)}")
                        
                        # Verificar se essas corridas aparecem na API
                        print(f"\n🔄 VERIFICAÇÃO: Por que essas corridas não aparecem na API?")
                        print(f"   • Corridas encontradas na VPS: {len(corridas_dia_20)}")
                        print(f"   • Data de scraping: {scraped_at}")
                        print(f"   • Source: {source}")
                        print(f"   • Tabela original: {table_name}")
                        
                        # Sugestão de investigação
                        print(f"\n💡 POSSÍVEIS CAUSAS:")
                        print(f"   1. API não está lendo da tabela 'rides_data' corretamente")
                        print(f"   2. Filtros de data na API podem estar incorretos") 
                        print(f"   3. Estrutura de dados na API não corresponde ao formato da VPS")
                        print(f"   4. Cache ou delay na sincronização dos dados")
                        
                    else:
                        print("❌ Nenhuma corrida do dia 20 encontrada após análise detalhada")
                        
                else:
                    print("❌ Estrutura 'newRecords' não encontrada no JSON")
        else:
            print("❌ Registro ID 16 não encontrado")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    process_rides_day_20()
