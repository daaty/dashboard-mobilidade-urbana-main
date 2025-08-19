import pandas as pd
import os

# Verificar arquivos Excel
excel_files = ['Dados Completos Motoristas.xlsx', 'CorridasConcluidas.xlsx', 'CorridasCanceladas.xlsx', 'CorridasPerdidas.xlsx']

for file in excel_files:
    if os.path.exists(file):
        print(f'=== {file} ===')
        try:
            df = pd.read_excel(file)
            print(f'Colunas: {list(df.columns)}')
            if 'Rating' in df.columns:
                print('Rating encontrado! Valores únicos:', df['Rating'].unique()[:10])
            else:
                # Buscar colunas com rating no nome
                rating_cols = [col for col in df.columns if 'rating' in col.lower() or 'avalia' in col.lower()]
                if rating_cols:
                    print('Colunas relacionadas a rating:', rating_cols)
                else:
                    print('Nenhuma coluna de rating encontrada')
            print()
        except Exception as e:
            print(f'Erro ao ler {file}: {e}')
            print()
