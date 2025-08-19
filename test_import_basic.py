#!/usr/bin/env python3
"""
Teste simples de importação
"""

import sys
import os
import pandas as pd

print("🔍 TESTE BÁSICO DE IMPORTAÇÃO")
print("=" * 40)

# Testar leitura da planilha
try:
    excel_file = "Dados Completos Motoristas.xlsx"
    print(f"📁 Testando leitura: {excel_file}")
    
    if not os.path.exists(excel_file):
        print(f"❌ Arquivo não encontrado: {excel_file}")
        exit(1)
    
    df = pd.read_excel(excel_file)
    print(f"✅ Planilha lida com sucesso!")
    print(f"📊 Linhas: {len(df)}")
    print(f"📋 Colunas: {len(df.columns)}")
    
    # Mostrar algumas colunas importantes
    key_columns = ['Driver ID', 'Driver Name', 'Phone Number', 'Success Rides', 'CITY']
    for col in key_columns:
        if col in df.columns:
            print(f"✅ Coluna '{col}': {df[col].count()} valores válidos")
        else:
            print(f"❌ Coluna '{col}': não encontrada")
    
    print("\n🎯 PRIMEIROS 3 REGISTROS:")
    for i, row in df.head(3).iterrows():
        driver_id = row.get('Driver ID', 'N/A')
        name = row.get('Driver Name', 'N/A')
        phone = row.get('Phone Number', 'N/A')
        rides = row.get('Success Rides', 0)
        city = row.get('CITY', 'N/A')
        print(f"   {i+1}. ID: {driver_id} | Nome: {name} | Telefone: {phone} | Corridas: {rides} | Cidade: {city}")
    
except Exception as e:
    print(f"💥 Erro: {str(e)}")
    
print("\n🚀 Teste básico concluído!")
