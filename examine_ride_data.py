#!/usr/bin/env python3
"""
Script para examinar detalhadamente os dados JSON na tabela rides_data
"""
import psycopg2
import json
from datetime import datetime

def examine_ride_data():
    DATABASE_URL = 'postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db'
    print(f'🔗 Conectando ao PostgreSQL na VPS para análise detalhada...')
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Pegar o registro mais recente
        cursor.execute("""
            SELECT 
                id,
                table_name,
                ride_data,
                scraped_at,
                session_info,
                source
            FROM rides_data 
            ORDER BY scraped_at DESC
            LIMIT 3;
        """)
        registros_recentes = cursor.fetchall()
        
        for registro in registros_recentes:
            id_reg = registro[0]
            table_name = registro[1]
            ride_data_str = registro[2]
            scraped_at = registro[3]
            session_info = registro[4]
            source = registro[5]
            
            print(f"\n" + "="*80)
            print(f"🔍 ANÁLISE DETALHADA - Registro ID: {id_reg}")
            print(f"📋 Table Name: {table_name}")
            print(f"🕐 Scraped At: {scraped_at}")
            print(f"📡 Source: {source}")
            print(f"🔗 Session Info: {session_info}")
            print("="*80)
            
            if ride_data_str:
                try:
                    ride_data = json.loads(ride_data_str)
                    print(f"✅ JSON válido - Tipo: {type(ride_data)}")
                    
                    # Imprimir estrutura completa do JSON
                    print(f"\n📊 ESTRUTURA COMPLETA DO JSON:")
                    print(json.dumps(ride_data, indent=2, ensure_ascii=False)[:2000])  # Primeiros 2000 chars
                    
                    if len(json.dumps(ride_data, indent=2)) > 2000:
                        print(f"... (truncado - total de {len(json.dumps(ride_data, indent=2))} caracteres)")
                    
                    # Analisar chaves principais
                    if isinstance(ride_data, dict):
                        print(f"\n🔑 CHAVES PRINCIPAIS:")
                        for key, value in ride_data.items():
                            if isinstance(value, list):
                                print(f"  • {key}: Lista com {len(value)} itens")
                                if len(value) > 0:
                                    print(f"    - Primeiro item: {type(value[0])} = {str(value[0])[:100]}")
                            elif isinstance(value, dict):
                                print(f"  • {key}: Dicionário com {len(value)} chaves: {list(value.keys())}")
                            else:
                                print(f"  • {key}: {type(value)} = {str(value)[:100]}")
                    
                    # Procurar por dados de corrida em estruturas aninhadas
                    def buscar_corridas_aninhadas(obj, path=""):
                        corridas_encontradas = []
                        
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                new_path = f"{path}.{key}" if path else key
                                
                                # Verificar se este objeto parece uma corrida
                                if isinstance(value, dict) and any(campo in value for campo in ['dt_corrida', 'hora', 'id_corrida', 'nome']):
                                    corridas_encontradas.append({
                                        'path': new_path,
                                        'corrida': value
                                    })
                                
                                # Buscar recursivamente
                                corridas_encontradas.extend(buscar_corridas_aninhadas(value, new_path))
                        
                        elif isinstance(obj, list):
                            for i, item in enumerate(obj):
                                new_path = f"{path}[{i}]"
                                
                                # Verificar se este item parece uma corrida
                                if isinstance(item, dict) and any(campo in item for campo in ['dt_corrida', 'hora', 'id_corrida', 'nome']):
                                    corridas_encontradas.append({
                                        'path': new_path,
                                        'corrida': item
                                    })
                                
                                # Buscar recursivamente
                                corridas_encontradas.extend(buscar_corridas_aninhadas(item, new_path))
                        
                        return corridas_encontradas
                    
                    print(f"\n🔍 BUSCANDO DADOS DE CORRIDAS ANINHADOS:")
                    corridas_aninhadas = buscar_corridas_aninhadas(ride_data)
                    
                    if corridas_aninhadas:
                        print(f"✅ Encontradas {len(corridas_aninhadas)} corridas nos dados!")
                        for idx, corrida_info in enumerate(corridas_aninhadas[:5]):  # Mostrar até 5
                            path = corrida_info['path']
                            corrida = corrida_info['corrida']
                            dt_corrida = corrida.get('dt_corrida', corrida.get('hora', 'N/A'))
                            nome = corrida.get('nome', 'N/A')
                            grupo = corrida.get('grupo', 'N/A')
                            cidade = corrida.get('cidade', 'N/A')
                            
                            print(f"  {idx+1}. Path: {path}")
                            print(f"     Corrida: {dt_corrida} | {nome} | {grupo} | {cidade}")
                            
                            # Verificar se é do dia 20
                            if '2025-08-20' in str(dt_corrida):
                                print(f"     ⭐ CORRIDA DO DIA 20 ENCONTRADA!")
                    else:
                        print("❌ Nenhuma corrida encontrada na estrutura de dados")
                
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao decodificar JSON: {e}")
                    print(f"📝 Conteúdo bruto:")
                    print(ride_data_str[:500])
            else:
                print("❌ Campo ride_data está vazio")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao conectar/consultar PostgreSQL: {e}")

if __name__ == "__main__":
    examine_ride_data()
