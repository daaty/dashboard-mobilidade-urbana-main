#!/usr/bin/env python3
"""
Script para verificar as datas das corridas no Excel
"""

import pandas as pd
from datetime import datetime, timedelta

def check_dates():
    """Verifica as datas das corridas no Excel"""
    
    print("📅 ANÁLISE DAS DATAS DAS CORRIDAS")
    print("=" * 50)
    
    if not pd.io.common.file_exists("CorridasConcluidas.xlsx"):
        print("❌ Arquivo Excel não encontrado!")
        return
    
    df = pd.read_excel("CorridasConcluidas.xlsx")
    print(f"📊 Total de registros: {len(df)}")
    
    # Procurar colunas de data
    date_columns = []
    for col in df.columns:
        if 'date' in col.lower() or 'data' in col.lower() or 'time' in col.lower() or 'hora' in col.lower():
            date_columns.append(col)
    
    print(f"📅 Colunas relacionadas a data: {date_columns}")
    
    # Analisar cada coluna de data
    for col in date_columns:
        print(f"\n🔍 Analisando coluna: {col}")
        print(f"   Tipo: {df[col].dtype}")
        print(f"   Valores únicos: {df[col].nunique()}")
        print(f"   Exemplos:")
        for i, val in enumerate(df[col].head(3)):
            print(f"     {i+1}. {val}")
        
        # Se for datetime, mostrar período
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            min_date = df[col].min()
            max_date = df[col].max()
            print(f"   📈 Período: {min_date} até {max_date}")
            
            # Verificar quantas corridas estão nos últimos 30 dias
            now = datetime.now()
            dt_30d = now - timedelta(days=30)
            recent = df[df[col] >= dt_30d]
            print(f"   📊 Corridas nos últimos 30 dias: {len(recent)}")
            
            dt_7d = now - timedelta(days=7)
            very_recent = df[df[col] >= dt_7d]
            print(f"   📊 Corridas nos últimos 7 dias: {len(very_recent)}")
            
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_rides = df[df[col] >= today]
            print(f"   📊 Corridas hoje: {len(today_rides)}")
    
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   O filtro de período está limitando os resultados!")
    print(f"   Para ver todas as 88 corridas, use um período maior ou")
    print(f"   ajuste o filtro para incluir o período de junho 2025.")

if __name__ == "__main__":
    check_dates()
