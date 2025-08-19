#!/usr/bin/env python3
"""
Script para analisar a estrutura da planilha 'Dados Completos Motoristas.xlsx'
e criar o mapeamento adequado para a tabela drivers_data
"""

import pandas as pd
import os
from datetime import datetime

def analyze_drivers_excel():
    """Analisa a estrutura da planilha de motoristas"""
    
    excel_file = "Dados Completos Motoristas .xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Arquivo '{excel_file}' não encontrado!")
        return
    
    print(f"📊 ANÁLISE DA PLANILHA: {excel_file}")
    print("=" * 60)
    
    try:
        # Ler o arquivo Excel
        print("📖 Lendo arquivo Excel...")
        df = pd.read_excel(excel_file)
        
        print(f"\n✅ Arquivo lido com sucesso!")
        print(f"📝 Total de linhas: {len(df)}")
        print(f"📝 Total de colunas: {len(df.columns)}")
        
        # Mostrar as colunas disponíveis
        print("\n📋 COLUNAS DISPONÍVEIS:")
        print("-" * 40)
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
        
        # Mostrar algumas linhas de exemplo
        print("\n📄 PRIMEIRAS 5 LINHAS:")
        print("-" * 40)
        print(df.head().to_string())
        
        # Mostrar tipos de dados
        print("\n🔍 TIPOS DE DADOS:")
        print("-" * 40)
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            null_count = len(df) - non_null
            print(f"{col:<25} | {dtype:<15} | Válidos: {non_null:<5} | Nulos: {null_count}")
        
        # Verificar valores únicos em algumas colunas
        print("\n📊 ANÁLISE DE VALORES ÚNICOS:")
        print("-" * 40)
        
        for col in df.columns:
            unique_count = df[col].nunique()
            print(f"{col:<25} | Valores únicos: {unique_count}")
            
            # Se tem poucos valores únicos, mostrar exemplos
            if unique_count <= 10 and unique_count > 0:
                unique_vals = df[col].dropna().unique()[:5]
                print(f"{'':>27} Exemplos: {list(unique_vals)}")
        
        # Sugerir mapeamento para drivers_data
        print("\n🎯 SUGESTÃO DE MAPEAMENTO PARA DRIVERS_DATA:")
        print("-" * 50)
        
        # Campos da tabela drivers_data
        drivers_fields = {
            'name': 'Nome do motorista',
            'phone': 'Telefone/Celular',
            'email': 'Email',
            'status': 'Status (ativo/inativo)',
            'rating': 'Avaliação/Rating',
            'total_rides': 'Total de corridas',
            'city': 'Cidade',
            'registration_date': 'Data de cadastro',
            'vehicle_type': 'Tipo de veículo',
            'vehicle_plate': 'Placa do veículo',
            'license_number': 'Número da CNH',
            'birth_date': 'Data de nascimento',
            'address': 'Endereço',
            'emergency_contact': 'Contato de emergência',
            'bank_account': 'Conta bancária',
            'earnings_total': 'Ganhos totais',
            'last_ride_date': 'Data da última corrida',
            'scraped_at': 'Data de importação'
        }
        
        # Tentar mapear automaticamente
        mapping_suggestions = {}
        for field, description in drivers_fields.items():
            print(f"\n{field:<20} ({description}):")
            
            # Buscar colunas similares
            similar_cols = []
            for col in df.columns:
                col_lower = col.lower()
                if field.lower() in col_lower or any(word in col_lower for word in field.split('_')):
                    similar_cols.append(col)
            
            if similar_cols:
                mapping_suggestions[field] = similar_cols[0]
                print(f"{'':>22} ✅ Sugestão: '{similar_cols[0]}'")
                if len(similar_cols) > 1:
                    print(f"{'':>22} 🔄 Alternativas: {similar_cols[1:]}")
            else:
                print(f"{'':>22} ❓ Não encontrado automaticamente")
        
        # Gerar código do mapeamento
        print("\n💻 CÓDIGO DE MAPEAMENTO SUGERIDO:")
        print("-" * 40)
        print("column_mapping = {")
        for field, col in mapping_suggestions.items():
            print(f"    '{field}': '{col}',")
        print("}")
        
        return df, mapping_suggestions
        
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {e}")
        return None, None

if __name__ == "__main__":
    analyze_drivers_excel()
