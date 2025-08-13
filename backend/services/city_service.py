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
    """Extrai cidades reais dos dados importados"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Buscar dados mais recentes
            result = conn.execute(text("SELECT ride_data FROM rides_data ORDER BY scraped_at DESC LIMIT 1"))
            row = result.fetchone()
            
            if not row:
                return []
            
            # Parse do JSON
            data = json.loads(row[0])
            records = data.get('newRecords', [])
            
            if not records:
                return []
            
            # A coluna "City" está na posição 15 (último índice) dos dados do Excel
            # Como vimos no script: ['MATUPA', 'PEIXOTO', 'GUARANTA DO NORTE']
            city_column_index = 15  # Último campo é a cidade
            
            # Extrair cidades únicas
            cities = set()
            for record in records:
                if len(record) > city_column_index and record[city_column_index]:
                    city = str(record[city_column_index]).strip()
                    if city and city.upper() != 'NAN' and city != '':
                        cities.add(city)
            
            return sorted(list(cities))
            
    except Exception as e:
        print(f"Erro ao extrair cidades: {e}")
        return []

# Adicionar esta função ao metrics.py
if __name__ == "__main__":
    cities = get_cities_from_rides_data()
    print(f"Cidades disponíveis: {cities}")
