import os
import asyncio
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL",
    "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db"
)

def extract_cities_from_rides_data():
    """Extrai cidades reais dos dados importados na tabela rides_data"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Buscar todos os dados da tabela rides_data
            result = conn.execute(text("SELECT ride_data FROM rides_data ORDER BY scraped_at DESC LIMIT 1"))
            row = result.fetchone()
            
            if not row:
                print("Nenhum dado encontrado na tabela rides_data")
                return []
            
            # Parse do JSON
            data = json.loads(row[0])
            records = data.get('newRecords', [])
            
            print(f"Processando {len(records)} registros...")
            
            # Assumindo que a coluna "City" é a 16ª coluna (index 15)
            cities = set()
            for record in records:
                if len(record) > 15 and record[15]:  # Coluna City
                    city = str(record[15]).strip().upper()
                    if city and city != 'NAN':
                        cities.add(city)
            
            cities_list = sorted(list(cities))
            print(f"Cidades encontradas: {cities_list}")
            return cities_list
            
    except Exception as e:
        print(f"Erro ao extrair cidades: {e}")
        return []

if __name__ == "__main__":
    cities = extract_cities_from_rides_data()
    print(f"\nCidades para usar no frontend: {cities}")
