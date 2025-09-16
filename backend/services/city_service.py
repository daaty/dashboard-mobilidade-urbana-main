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

# Mapeamento de nomes de cidades para padronização
CITY_MAPPING = {
    # Mato Grosso - Cidades adicionais encontradas
    "NOVA BANDEIRANTES": "NOVA BANDEIRANTES",
    "NOVA MONTE VERDE": "NOVA MONTE VERDE",
    "BANDEIRANTES": "BANDEIRANTES",
    "MONTE VERDE": "NOVA MONTE VERDE",
        # Mato Grosso
    "MATUPA": "MATUPA",
    "MATUPÁ": "MATUPA",
    "Matupá": "MATUPA",
    "Matupa": "MATUPA",
    "PEIXOTO": "PEIXOTO DE AZEVEDO",
    "PEIXOTO DE AZEVEDO": "PEIXOTO DE AZEVEDO",
    "GUARANTA": "GUARANTA DO NORTE",
    "GUARANTA DO NORTE": "GUARANTA DO NORTE",
    "NOVA MARINGA": "NOVA MARINGÁ",
    "NOVA MARINGÁ": "NOVA MARINGÁ",
    "NOVA MARINGA": "NOVA MARINGÁ",
    "SORRISO": "SORRISO",
    "SINOP": "SINOP",
    "CUIABA": "CUIABÁ",
    "CUIABÁ": "CUIABÁ",
    "VARZEA GRANDE": "VÁRZEA GRANDE",
    "VÁRZEA GRANDE": "VÁRZEA GRANDE",
    "RONDONOPOLIS": "RONDONÓPOLIS",
    "RONDONÓPOLIS": "RONDONÓPOLIS",
    "BARRA DO GARCAS": "BARRA DO GARÇAS",
    "BARRA DO GARÇAS": "BARRA DO GARÇAS",
    "ALTO GARCAS": "ALTO GARÇAS",
    "ALTO GARÇAS": "ALTO GARÇAS",
    "ARAPUTANGA": "ARAPUTANGA",
    "CAMPO VERDE": "CAMPO VERDE",
    "CHAPADA DOS GUIMARAES": "CHAPADA DOS GUIMARÃES",
    "CHAPADA DOS GUIMARÃES": "CHAPADA DOS GUIMARÃES",
    "DIAMANTINO": "DIAMANTINO",
    "JACIARA": "JACIARA",
    "JUARA": "JUARA",
    "LUCAS DO RIO VERDE": "LUCAS DO RIO VERDE",
    "NOVA MUTUM": "NOVA MUTUM",
    "NOVA XAVANTINA": "NOVA XAVANTINA",
    "PONTAL DO ARAGUAIA": "PONTAL DO ARAGUAIA",
    "PRIMAVERA DO LESTE": "PRIMAVERA DO LESTE",
    "SANTO ANTONIO DO LEVERGER": "SANTO ANTÔNIO DO LEVERGER",
    "SANTO ANTÔNIO DO LEVERGER": "SANTO ANTÔNIO DO LEVERGER",
    "SAO FELIX DO ARAGUAIA": "SÃO FÉLIX DO ARAGUAIA",
    "SÃO FÉLIX DO ARAGUAIA": "SÃO FÉLIX DO ARAGUAIA",
    "TANGARA DA SERRA": "TANGARÁ DA SERRA",
    "TANGARÁ DA SERRA": "TANGARÁ DA SERRA",
    "TERRA NOVA DO NORTE": "TERRA NOVA DO NORTE",
    "UNIAO DO SUL": "UNIÃO DO SUL",
    "UNIÃO DO SUL": "UNIÃO DO SUL",
    "VALE DE SAO DOMINGOS": "VALE DE SÃO DOMINGOS",
    "VALE DE SÃO DOMINGOS": "VALE DE SÃO DOMINGOS",
    "VERA": "VERA",
    "VILA RICA": "VILA RICA",

    # Outros estados
    "BRASILIA": "BRASÍLIA",
    "BRASÍLIA": "BRASÍLIA",
    "GOIANIA": "GOIÂNIA",
    "GOIÂNIA": "GOIÂNIA",
    "PALMAS": "PALMAS",
    "RIO DE JANEIRO": "RIO DE JANEIRO",
    "SAO PAULO": "SÃO PAULO",
    "SÃO PAULO": "SÃO PAULO",
    "BELO HORIZONTE": "BELO HORIZONTE",
    "SALVADOR": "SALVADOR",
    "FORTALEZA": "FORTALEZA",
    "RECIFE": "RECIFE",
    "PORTO ALEGRE": "PORTO ALEGRE",
    "CURITIBA": "CURITIBA",
    "FLORIANOPOLIS": "FLORIANÓPOLIS",
    "FLORIANÓPOLIS": "FLORIANÓPOLIS",
    "MANAUS": "MANAUS",
    "BELEM": "BELÉM",
    "BELÉM": "BELÉM",
    "JOÃO PESSOA": "JOÃO PESSOA",
    "JOÃO PESSOA": "JOÃO PESSOA",
    "ARACAJU": "ARACAJU",
    "MACEIO": "MACEIÓ",
    "MACEIÓ": "MACEIÓ",
    "TERESINA": "TERESINA",
    "SAO LUIS": "SÃO LUÍS",
    "SÃO LUÍS": "SÃO LUÍS",
    "NATAL": "NATAL",
    "VITORIA": "VITÓRIA",
    "VITÓRIA": "VITÓRIA",
    "CAMPO GRANDE": "CAMPO GRANDE",
    "CUIABA": "CUIABÁ",
    "CUIABÁ": "CUIABÁ",
    "PORTO VELHO": "PORTO VELHO",
    "BOA VISTA": "BOA VISTA",
    "RIO BRANCO": "RIO BRANCO",
    "MACAPA": "MACAPÁ",
    "MACAPÁ": "MACAPÁ",
    "PALMAS": "PALMAS"
}

def extract_city_from_address(address_str):
    """Extrai nome da cidade de um endereço completo"""
    if not address_str:
        return None

    address = str(address_str).strip()

    # Padrões comuns de endereços brasileiros
    # 1. Padrão: "Rua X, Cidade - UF, CEP, País"
    # 2. Padrão: "Cidade, Estado, País"
    # 3. Padrão: "Endereço, Cidade - UF"

    # Tentar extrair cidade de padrões comuns
    import re

    # Padrão 1: "Cidade - UF" (mais comum)
    city_uf_match = re.search(r'([^-]+)\s*-\s*([A-Z]{2})', address)
    if city_uf_match:
        city_part = city_uf_match.group(1).strip()
        # Tentar normalizar a cidade encontrada
        normalized = normalize_city_name(city_part)
        if normalized:
            return normalized

    # Padrão 2: Procurar por cidades conhecidas no endereço
    known_cities = [
        "PEIXOTO DE AZEVEDO", "NOVA MONTE VERDE", "GUARANTA DO NORTE",
        "NOVA BANDEIRANTES", "MATUPA", "MATUPÁ", "PEIXOTO", "GUARANTA"
    ]

    address_upper = address.upper()
    for city in known_cities:
        if city in address_upper:
            return normalize_city_name(city)

    # Padrão 3: Último recurso - tentar extrair palavras que parecem cidades
    # (palavras com mais de 3 letras que não contenham números)
    words = re.findall(r'\b[A-Za-zÀ-ÿ]{4,}\b', address)
    for word in words:
        if not any(char.isdigit() for char in word):  # Não contém números
            normalized = normalize_city_name(word)
            if normalized:
                return normalized

    return None

def normalize_city_name(city_name):
    """Normaliza o nome da cidade aplicando mapeamento e limpeza"""
    if not city_name:
        return None

    # Limpar e padronizar
    city = str(city_name).strip().upper()

    # Remover valores inválidos comuns
    invalid_values = [
        'NAN', 'N/A', '--', 'UNNAMED', '', 'NULL', 'NONE', 'UNDEFINED',
        'BOOK RIDE', 'CANCEL RIDE', 'MISS RIDE', 'RIDE', 'CORRIDA',
        'COMPLETED', 'CANCELLED', 'MISSED', 'RIDE COMPLETED', 'RIDE CANCELLED',
        'RIDE MISSED', 'CORRIDA CONCLUÍDA', 'CORRIDA CANCELADA', 'CORRIDA PERDIDA'
    ]

    if city in invalid_values or len(city) < 3:
        return None

    # Verificar se contém apenas números
    if city.isdigit():
        return None

    # Aplicar mapeamento
    if city in CITY_MAPPING:
        return CITY_MAPPING[city]

    # Se não estiver no mapeamento, verificar se é uma cidade válida
    # Remover acentos e caracteres especiais para comparação
    normalized = city.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
    normalized = normalized.replace('Â', 'A').replace('Ê', 'E').replace('Ô', 'O')
    normalized = normalized.replace('Ã', 'A').replace('Õ', 'O').replace('Ç', 'C')

    # Verificar se está no mapeamento após normalização
    if normalized in CITY_MAPPING:
        return CITY_MAPPING[normalized]

    # DETECTAR ENDEREÇOS COMPLETOS - não retornar como "cidade válida"
    # Padrões que indicam que é um endereço, não uma cidade simples:
    address_indicators = [
        ',',  # Várias partes separadas por vírgula
        '-',  # Padrão "Cidade - UF"
        ' R.', ' AV.', ' AV ', ' RUA ', ' TRAVESSA ',  # Abreviações de logradouro
        ' NÚMERO ', ' N ', ' Nº ', ' NUM ',  # Indicadores de número
        ' CENTRO ', ' BAIRRO ', ' SETOR ',  # Partes de endereço
        ' CEP', ' BRASIL', ' MT', ' MS', ' GO'  # CEP, país, estados
    ]

    # Se contém indicadores de endereço, não é uma cidade simples
    if any(indicator in city for indicator in address_indicators):
        return None

    # Se é muito longo (mais de 30 caracteres), provavelmente é um endereço
    if len(city) > 30:
        return None

    # Se não estiver no mapeamento, retornar o nome original limpo
    # Mas garantir que seja title case para consistência
    return city.title() if len(city) > 2 else None

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

                        # Aplicar normalização
                        normalized_city = normalize_city_name(city)
                        if normalized_city:
                            cities.add(normalized_city)

                except Exception as e:
                    print(f"Erro ao processar registro: {e}")
                    continue

            # Adicionar cidades da tabela driver_personal_details
            try:
                driver_cities_result = conn.execute(text("SELECT DISTINCT city FROM driver_personal_details"))
                driver_cities = driver_cities_result.fetchall()
                
                for city_row in driver_cities:
                    city_name = city_row[0]
                    if city_name:
                        normalized_driver_city = normalize_city_name(city_name)
                        if normalized_driver_city:
                            cities.add(normalized_driver_city)
                            
            except Exception as e:
                print(f"Aviso: Não foi possível consultar driver_personal_details: {e}")
            
            # Remover duplicatas considerando case-insensitive e manter apenas a versão normalizada
            final_cities = set()
            cities_list = list(cities)
            
            for city in cities_list:
                # Verificar se já existe uma versão normalizada desta cidade
                city_upper = city.upper()
                found_normalized = False
                
                for existing_city in final_cities:
                    if existing_city.upper() == city_upper:
                        found_normalized = True
                        break
                
                if not found_normalized:
                    final_cities.add(city)
            
            return sorted(list(final_cities))

    except Exception as e:
        print(f"Erro ao extrair cidades: {e}")
        return []

# Adicionar esta função ao metrics.py
if __name__ == "__main__":
    cities = get_cities_from_rides_data()
    print(f"Cidades disponíveis ({len(cities)}): {cities}")

    # Análise detalhada dos dados
    print("\n🔍 ANÁLISE DETALHADA DOS DADOS:")
    print("=" * 80)

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT ride_data FROM rides_data"))
            rows = result.fetchall()

            print(f"📊 Total de registros na tabela: {len(rows)}")

            table_counts = {}
            city_counts = {}

            for row in rows:
                try:
                    data = json.loads(row[0])
                    table_name = data.get("tableName", "")
                    records = data.get("newRecords", [])

                    if table_name not in table_counts:
                        table_counts[table_name] = 0
                    table_counts[table_name] += len(records)

                    # Contar cidades por tipo
                    for record in records:
                        city = None

                        if table_name == "Completed Rides" and len(record) > 15:
                            city = record[15]
                        elif table_name == "Cancelled Rides" and len(record) > 17:
                            city = record[17]
                        elif table_name == "Missed Rides" and len(record) > 8:
                            city = record[8]

                        if city:
                            normalized_city = normalize_city_name(city)
                            if normalized_city:
                                if normalized_city not in city_counts:
                                    city_counts[normalized_city] = {"total": 0, "tipos": {}}
                                city_counts[normalized_city]["total"] += 1

                                if table_name not in city_counts[normalized_city]["tipos"]:
                                    city_counts[normalized_city]["tipos"][table_name] = 0
                                city_counts[normalized_city]["tipos"][table_name] += 1

                except Exception as e:
                    continue

            print("\n📋 DISTRIBUIÇÃO POR TIPO DE CORRIDA:")
            for table_name, count in table_counts.items():
                print(f"   {table_name}: {count} registros")

            print("\n🏙️ CIDADES ENCONTRADAS:")
            for city, data in sorted(city_counts.items()):
                tipos_str = ", ".join([f"{tipo}: {count}" for tipo, count in data["tipos"].items()])
                print(f"   {city}: {data['total']} registros ({tipos_str})")

            # Verificar cidades na tabela driver_personal_details
            print("\n🔍 VERIFICANDO CIDADES EM DRIVER_PERSONAL_DETAILS:")
            try:
                driver_cities_result = conn.execute(text("SELECT DISTINCT city FROM driver_personal_details ORDER BY city"))
                driver_cities = driver_cities_result.fetchall()

                if driver_cities:
                    print(f"📍 Cidades encontradas em driver_personal_details: {len(driver_cities)}")
                    for city_row in driver_cities:
                        city_name = city_row[0]
                        if city_name:
                            normalized_driver_city = normalize_city_name(city_name)
                            if normalized_driver_city and normalized_driver_city not in cities:
                                print(f"   ➕ Cidade adicional encontrada: {normalized_driver_city} (original: {city_name})")
                                cities.add(normalized_driver_city)
                else:
                    print("❌ Nenhuma cidade encontrada em driver_personal_details")

            except Exception as e:
                print(f"Erro ao consultar driver_personal_details: {e}")

            # Atualizar a lista final de cidades
            final_cities = sorted(list(cities))
            print(f"\n✅ TOTAL FINAL DE CIDADES: {len(final_cities)}")
            print("🏙️ LISTA COMPLETA:", final_cities)

    except Exception as e:
        print(f"Erro na análise detalhada: {e}")
