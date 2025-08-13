import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
).replace("postgresql+asyncpg://", "postgresql://")

def get_cities_from_rides_data():
    """Extrai cidades reais dos dados importados de todos os tipos de corrida"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Buscar todos os dados
            result = conn.execute(text("SELECT ride_data FROM rides_data"))
            rows = result.fetchall()
            
            if not rows:
                return []
            
            cities = set()
            
            for row in rows:
                try:
                    # Parse do JSON
                    data = json.loads(row[0])
                    table_name = data.get('tableName', '')
                    records = data.get('newRecords', [])
                    
                    if not records:
                        continue
                    
                    # Extrair cidades baseado no tipo de corrida
                    for record in records:
                        city = None
                        
                        if table_name == "Completed Rides" and len(record) > 15:
                            city = record[15]  # Índice 15 para corridas concluídas
                        elif table_name == "Cancelled Rides" and len(record) > 17:
                            city = record[17]  # Índice 17 para corridas canceladas
                        elif table_name == "Missed Rides" and len(record) > 8:
                            city = record[8]   # Índice 8 para corridas perdidas
                        
                        if city:
                            city = str(city).strip()
                            if city and city.upper() != 'NAN' and city != '' and city != '--' and city != 'Unnamed':
                                cities.add(city)
                                
                except Exception as e:
                    print(f"Erro ao processar registro: {e}")
                    continue
            
            return sorted(list(cities))
            
    except Exception as e:
        print(f"Erro ao extrair cidades: {e}")
        return []

# Adicionar esta função ao metrics.py
if __name__ == "__main__":
    cities = get_cities_from_rides_data()
    print(f"Cidades disponíveis: {cities}")
