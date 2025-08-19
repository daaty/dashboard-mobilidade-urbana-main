import pandas as pd
import psycopg2
import json
import os
from datetime import datetime

def consolidar_ratings_motoristas():
    """
    Consolida os ratings das corridas concluídas com os dados dos motoristas
    """
    print("=== CONSOLIDANDO RATINGS DOS MOTORISTAS ===")
    
    # Ler dados das corridas concluídas
    df_corridas = pd.read_excel('CorridasConcluidas.xlsx')
    print(f"Total de corridas: {len(df_corridas)}")
    
    # Ler dados dos motoristas
    df_motoristas = pd.read_excel('Dados Completos Motoristas.xlsx')
    print(f"Total de registros de motoristas: {len(df_motoristas)}")
    
    # Processar ratings por motorista
    df_corridas_numeric = df_corridas.copy()
    df_corridas_numeric['Rating_Numeric'] = pd.to_numeric(df_corridas_numeric['Rating'], errors='coerce')
    
    # Calcular rating médio por motorista
    rating_por_motorista = df_corridas_numeric[df_corridas_numeric['Rating_Numeric'].notna()].groupby('Driver Name')['Rating_Numeric'].agg(['count', 'mean', 'std']).round(2)
    rating_por_motorista.columns = ['total_ratings', 'avg_rating', 'rating_std']
    rating_por_motorista['rating_std'] = rating_por_motorista['rating_std'].fillna(0)
    
    print(f"Motoristas com ratings: {len(rating_por_motorista)}")
    print("\nRatings por motorista:")
    print(rating_por_motorista)
    
    # Conectar ao PostgreSQL e atualizar dados
    try:
        conn = psycopg2.connect(
            host='148.230.73.27', 
            user='n8n_user', 
            database='n8n',
            password='123mudar'
        )
        cur = conn.cursor()
        
        # Buscar motoristas existentes no banco
        cur.execute("SELECT driver_id, additional_data FROM drivers LIMIT 50")
        drivers_db = cur.fetchall()
        
        updated_count = 0
        for driver_id, additional_data in drivers_db:
            if additional_data and 'profile' in additional_data:
                driver_name = additional_data['profile'].get('driver_name', '')
                
                # Buscar rating para este motorista
                if driver_name in rating_por_motorista.index:
                    rating_info = rating_por_motorista.loc[driver_name]
                    
                    # Atualizar additional_data com informações de rating
                    additional_data['rating_info'] = {
                        'avg_rating': float(rating_info['avg_rating']),
                        'total_ratings': int(rating_info['total_ratings']),
                        'rating_std': float(rating_info['rating_std']),
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    # Se raw_data existe, adicionar lá também
                    if 'raw_data' in additional_data:
                        additional_data['raw_data']['Rating'] = float(rating_info['avg_rating'])
                    
                    # Atualizar no banco
                    cur.execute(
                        "UPDATE drivers SET additional_data = %s WHERE driver_id = %s",
                        (json.dumps(additional_data), driver_id)
                    )
                    updated_count += 1
                    
                    print(f"Atualizado: {driver_name} (ID: {driver_id}) - Rating: {rating_info['avg_rating']}")
        
        conn.commit()
        conn.close()
        
        print(f"\n=== RESUMO ===")
        print(f"Motoristas atualizados: {updated_count}")
        print("Ratings consolidados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao conectar/atualizar banco: {e}")
        return False
    
    return True

if __name__ == "__main__":
    consolidar_ratings_motoristas()
