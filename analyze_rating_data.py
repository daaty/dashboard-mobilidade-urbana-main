import pandas as pd
import numpy as np

# Verificar os dados de rating nas corridas concluídas
df_corridas = pd.read_excel('CorridasConcluidas.xlsx')
print('=== DADOS DE RATING DAS CORRIDAS CONCLUÍDAS ===')
print(f'Total de corridas: {len(df_corridas)}')
print(f'Corridas com rating: {df_corridas["Rating"].notna().sum()}')

# Verificar tipos de rating
ratings = df_corridas['Rating'].dropna()
print(f'Tipos únicos de rating: {[type(x).__name__ for x in ratings.unique()]}')
print(f'Valores únicos de rating: {list(ratings.unique())}')

# Filtrar apenas ratings numéricos
numeric_ratings = pd.to_numeric(df_corridas['Rating'], errors='coerce').dropna()
print(f'Ratings numéricos válidos: {len(numeric_ratings)}')
if len(numeric_ratings) > 0:
    print(f'Ratings numéricos únicos: {sorted(numeric_ratings.unique())}')
    print(f'Rating médio: {numeric_ratings.mean():.2f}')

print()
print('=== EXEMPLOS DE CORRIDAS COM RATING ===')
corridas_com_rating = df_corridas[df_corridas['Rating'].notna()].head(10)
for index, row in corridas_com_rating.iterrows():
    print(f'Driver: {row["Driver Name"]} | Rating: {row["Rating"]} | Data: {row["Pickup Time"]}')

print()
print('=== ANÁLISE POR MOTORISTA ===')
# Converter ratings para numérico para cálculo da média
df_corridas_numeric = df_corridas.copy()
df_corridas_numeric['Rating_Numeric'] = pd.to_numeric(df_corridas_numeric['Rating'], errors='coerce')
rating_por_motorista = df_corridas_numeric[df_corridas_numeric['Rating_Numeric'].notna()].groupby('Driver Name')['Rating_Numeric'].agg(['count', 'mean']).round(2)
print(rating_por_motorista.head(10))
