#!/usr/bin/env python3

import pandas as pd
import os
from datetime import datetime, timedelta

def analisar_corridas_xlsx():
    """Analisar arquivos XLSX de corridas para ver quantas corridas concluídas existem"""
    
    arquivos = [
        'CorridasConcluidas.xlsx',
        'CorridasCanceladas.xlsx', 
        'CorridasPerdidas.xlsx'
    ]
    
    print("🔍 ANÁLISE DOS ARQUIVOS XLSX DE CORRIDAS")
    print("=" * 60)
    
    total_geral = {
        'concluidas': 0,
        'canceladas': 0,
        'perdidas': 0
    }
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            print(f"\n📊 Analisando: {arquivo}")
            try:
                # Ler o arquivo Excel
                df = pd.read_excel(arquivo)
                
                print(f"   📈 Total de registros: {len(df)}")
                print(f"   📋 Colunas disponíveis: {list(df.columns)}")
                
                # Verificar se há dados de data
                colunas_data = [col for col in df.columns if any(palavra in col.lower() for palavra in ['data', 'date', 'hora', 'time'])]
                if colunas_data:
                    print(f"   📅 Colunas de data encontradas: {colunas_data}")
                    
                    # Tentar analisar datas
                    for col_data in colunas_data:
                        try:
                            df[col_data] = pd.to_datetime(df[col_data], errors='coerce')
                            datas_validas = df[col_data].dropna()
                            if len(datas_validas) > 0:
                                data_min = datas_validas.min()
                                data_max = datas_validas.max()
                                print(f"      Período: {data_min.strftime('%Y-%m-%d')} até {data_max.strftime('%Y-%m-%d')}")
                                
                                # Verificar corridas do dia 20/08/2025
                                data_20_ago = datetime(2025, 8, 20)
                                corridas_dia_20 = df[df[col_data].dt.date == data_20_ago.date()]
                                if len(corridas_dia_20) > 0:
                                    print(f"      🎯 Corridas do dia 20/08/2025: {len(corridas_dia_20)}")
                                
                                # Verificar últimos 30 dias
                                hoje = datetime.now()
                                data_30_dias = hoje - timedelta(days=30)
                                corridas_30d = df[df[col_data] >= data_30_dias]
                                print(f"      📊 Corridas últimos 30 dias: {len(corridas_30d)}")
                                break
                        except Exception as e:
                            print(f"      ❌ Erro ao processar coluna {col_data}: {e}")
                
                # Mostrar algumas amostras
                if len(df) > 0:
                    print(f"   🔍 Amostra dos dados:")
                    print(df.head(3).to_string(max_cols=8))
                
                # Atualizar totais
                tipo = None
                if 'concluidas' in arquivo.lower():
                    total_geral['concluidas'] = len(df)
                    tipo = 'concluidas'
                elif 'canceladas' in arquivo.lower():
                    total_geral['canceladas'] = len(df)
                    tipo = 'canceladas'
                elif 'perdidas' in arquivo.lower():
                    total_geral['perdidas'] = len(df)
                    tipo = 'perdidas'
                
                print(f"   ✅ Tipo: {tipo} - Total: {len(df)} registros")
                
            except Exception as e:
                print(f"   ❌ Erro ao ler {arquivo}: {e}")
        else:
            print(f"\n❌ Arquivo não encontrado: {arquivo}")
    
    print("\n" + "=" * 60)
    print("📋 RESUMO GERAL DOS ARQUIVOS XLSX:")
    print(f"✅ Corridas Concluídas: {total_geral['concluidas']}")
    print(f"❌ Corridas Canceladas: {total_geral['canceladas']}")
    print(f"⏸️  Corridas Perdidas: {total_geral['perdidas']}")
    print(f"📊 TOTAL: {sum(total_geral.values())}")
    
    print(f"\n🔍 COMPARAÇÃO COM O QUE A API MOSTRA:")
    print(f"   API mostra apenas 2 corridas concluídas (do scraper)")
    print(f"   Mas há {total_geral['concluidas']} corridas concluídas no XLSX!")
    print(f"   DIFERENÇA: {total_geral['concluidas'] - 2} corridas NÃO estão sendo contabilizadas!")

if __name__ == "__main__":
    analisar_corridas_xlsx()
