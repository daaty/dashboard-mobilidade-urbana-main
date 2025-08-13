#!/usr/bin/env python3
"""
Script para verificar o mapeamento correto das colunas do Excel
"""

import pandas as pd

def check_excel_structure():
    """Verifica a estrutura do Excel para mapear corretamente"""
    
    try:
        print("📊 Analisando estrutura do Excel...")
        df = pd.read_excel("CorridasConcluidas.xlsx")
        
        print(f"✅ Arquivo lido: {len(df)} registros, {len(df.columns)} colunas")
        print("\n🏗️ Estrutura das colunas:")
        
        for i, col in enumerate(df.columns):
            print(f"  {i:2d}: {col}")
            
        print("\n📝 Primeiro registro como exemplo:")
        first_row = df.iloc[0]
        for i, col in enumerate(df.columns):
            value = first_row[col]
            print(f"  {i:2d}: {col} = {value}")
            
        # Identificar colunas importantes
        print("\n🎯 Mapeamento importante:")
        for i, col in enumerate(df.columns):
            if 'nome' in col.lower() or 'name' in col.lower():
                print(f"  NOME: índice {i} - {col}")
            elif 'telefone' in col.lower() or 'phone' in col.lower():
                print(f"  TELEFONE: índice {i} - {col}")
            elif 'city' in col.lower() or 'cidade' in col.lower():
                print(f"  CIDADE: índice {i} - {col}")
            elif 'status' in col.lower():
                print(f"  STATUS: índice {i} - {col}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_excel_structure()
