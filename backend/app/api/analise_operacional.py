from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from typing import Optional, List, Dict
import json
from collections import defaultdict
from datetime import datetime, timedelta
import re

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

def extract_datetime_from_record(rec, index):
    """Extrai data/hora de um registro, lidando com AMBOS os formatos (scraper + frontend)"""
    if index >= len(rec):
        return None

    value = str(rec[index]).strip()

    # Formato do scraper: "202508202025-08-20 16:59:50"
    scraper_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", value)
    if scraper_match:
        return scraper_match.group(1)

    # Formato do frontend: "2025-08-20 16:59:50" (sem prefixo)
    frontend_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", value)
    if frontend_match:
        return frontend_match.group(1)

    return None

def is_valid_address(address_str):
    """
    Valida se uma string parece ser um endereço válido
    Melhorada para aceitar endereços de Mato Grosso e Plus Codes
    """
    if not address_str:
        return False

    address = str(address_str).strip()

    # Rejeitar strings muito curtas (provavelmente não são endereços)
    if len(address) < 5:
        return False

    address_lower = address.lower()

    # Rejeitar padrões que DEFINITIVAMENTE não são endereços
    invalid_patterns = [
        r'^\d{10,}$',      # Apenas números longos (IDs)
        r'^\+\d{10,}$',    # Telefone internacional longo
        r'^\d{8,11}$',     # Telefone brasileiro (8-11 dígitos)
        r'^nan$',          # Valor nulo
        r'^--$',           # Placeholder
        r'^none$',         # None value
        r'^null$',         # Null value
        r'^\s*$',          # String vazia
        r'^unnamed$',      # Unnamed
        r'^unknown$',      # Unknown
        r'^n/a$',          # N/A
    ]

    for pattern in invalid_patterns:
        if re.match(pattern, address_lower):
            return False

    # ACEITAR se tem estrutura de endereço geográfico
    # 1. Contém indicadores de endereço (expandido para Mato Grosso)
    address_indicators = [
        'rua', 'avenida', 'av.', 'alameda', 'travessa', 'praça',
        'bairro', 'centro', 'vila', 'jardim', 'parque',
        'setor', 'loteamento', 'condomínio', 'residencial',
        'estrada', 'rodovia', 'km', 'número', 'n°', 'nº',
        'hospital', 'shopping', 'supermercado', 'farmacia',
        'escola', 'universidade', 'aeroporto', 'rodoviária',
        'cidade', 'município', 'distrito', 'zona',
        # Indicadores específicos de Mato Grosso
        'linha', 'ramal', 'sítio', 'fazenda', 'chácara',
        'comunidade', 'aglomeração', 'povoado', 'aldeia'
    ]

    has_address_indicator = any(indicator in address_lower for indicator in address_indicators)

    # 2. Tem formato estruturado (separado por vírgulas)
    has_comma_structure = ',' in address and len(address.split(',')) >= 2

    # 3. Contém nome de cidade/estado brasileiro (expandido)
    brazilian_locations = [
        'mato grosso', 'nova bandeirantes', 'peixoto de azevedo',
        'nova monte verde', 'guarantã do norte', 'brasil',
        'acre', 'alagoas', 'amapá', 'amazonas', 'bahia', 'ceará',
        'distrito federal', 'espírito santo', 'goiás', 'maranhão',
        'mato grosso do sul', 'minas gerais', 'pará', 'paraíba',
        'paraná', 'pernambuco', 'piauí', 'rio de janeiro',
        'rio grande do norte', 'rio grande do sul', 'rondônia',
        'roraima', 'santa catarina', 'são paulo', 'sergipe', 'tocantins',
        # Cidades específicas de Mato Grosso
        'cuiabá', 'várzea grande', 'rondonópolis', 'sinop',
        'tangará da serra', 'sorriso', 'cáceres', 'barra do garças'
    ]

    has_brazilian_location = any(location in address_lower for location in brazilian_locations)

    # 4. Parece coordenada geográfica (latitude,longitude)
    is_coordinate = bool(re.match(r'^-?\d+\.\d+,\s*-?\d+\.\d+$', address.strip()))

    # 5. Parece código Plus Code do Google (formato como 2G9F+68)
    is_plus_code = bool(re.match(r'^[A-Z0-9]{4,8}\+[A-Z0-9]{2,3}', address))

    # 6. Parece endereço estruturado (número + nome + cidade)
    # Exemplo: "1250, Rua Curitiba, Jardim Vitória"
    is_structured_address = bool(re.match(r'^\d+\s*,?\s*[A-Za-zÀ-ÿ]', address))

    # ACEITAR se qualquer uma das condições for verdadeira
    return (has_address_indicator or
            has_comma_structure or
            has_brazilian_location or
            is_coordinate or
            is_plus_code or
            is_structured_address)

def parse_address_components(address_str):
    """
    Tenta extrair componentes do endereço (cidade, estado) de uma string de endereço
    """
    if not address_str:
        return None, None, None

    address = str(address_str).strip()

    # Tentar extrair cidade e estado de padrões comuns
    # Padrão: "Endereço, Cidade, Estado, País"
    parts = [part.strip() for part in address.split(',')]

    cidade = None
    estado = None
    endereco_clean = address

    if len(parts) >= 3:
        # Última parte pode ser país
        if 'brasil' in parts[-1].lower():
            parts = parts[:-1]

        if len(parts) >= 2:
            # Penúltima parte pode ser estado
            estado_part = parts[-1]
            if len(estado_part) <= 3:  # Sigla do estado
                estado = estado_part.upper()
                parts = parts[:-1]

            # Última parte restante é provavelmente cidade
            if parts:
                cidade = parts[-1]
                endereco_clean = ', '.join(parts[:-1])

    return endereco_clean, cidade, estado

def get_period_filter(periodo: str):
    """Retorna os filtros de data baseados no período selecionado"""
    now = datetime.now()

    if periodo == "hoje":
        dt_ini = now.replace(hour=0, minute=0, second=0, microsecond=0)
        dt_fim = now
    elif periodo == "7d":
        dt_ini = now - timedelta(days=7)
        dt_fim = now
    elif periodo == "30d":
        dt_ini = now - timedelta(days=30)
        dt_fim = now
    elif periodo == "3m":
        dt_ini = now - timedelta(days=90)
        dt_fim = now
    elif periodo == "6m":
        dt_ini = now - timedelta(days=180)
        dt_fim = now
    elif periodo == "12m":
        dt_ini = now - timedelta(days=365)
        dt_fim = now
    else:
        # Default para 30 dias
        dt_ini = now - timedelta(days=30)
        dt_fim = now

    return dt_ini, dt_fim

@router.get("/mapa-calor-problemas")
async def get_mapa_calor_problemas(
    db: AsyncSession = Depends(get_db),
    periodo: str = Query("30d", enum=["hoje", "7d", "30d", "3m", "6m", "12m"]),
    cidade: Optional[str] = Query(None)
):
    """
    Retorna dados para o mapa de calor de problemas operacionais

    - **periodo**: Período de análise (hoje, 7d, 30d, 3m, 6m, 12m)
    - **cidade**: Filtro opcional por cidade
    """
    try:
        # Obter filtros de período
        dt_ini, dt_fim = get_period_filter(periodo)

        result = await db.execute(select(RidesData))
        rides = result.scalars().all()

        pontos = []
        total_registros = 0
        ids_processados = set()  # Set para deduplicação por ID único

        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except Exception:
                    continue

            table_name = ride_data.get("tableName", "")
            new_records = ride_data.get("newRecords", [])

            # Processar diferentes tipos de registros
            if table_name in ["Cancelled Rides", "corridas_canceladas"]:
                for rec in new_records:
                    total_registros += 1

                    # Extrair ID único para deduplicação
                    id_corrida = rec[0] if len(rec) > 0 else None
                    
                    # DEDUPLICAÇÃO: Pular se ID já foi processado
                    if id_corrida in ids_processados:
                        continue

                    # Tentar extrair data para filtro temporal
                    dt_corrida = None
                    for idx in [12, 11, 8, 7]:  # Possíveis índices de data
                        if idx < len(rec) and rec[idx]:
                            dt_str = extract_datetime_from_record([rec[idx]], 0)
                            if dt_str:
                                try:
                                    dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                    break
                                except Exception:
                                    continue

                    # Aplicar filtro temporal
                    if dt_corrida and not (dt_ini <= dt_corrida <= dt_fim):
                        continue

                    # CORREÇÃO: Usar a MESMA lógica sofisticada do endpoint de métricas
                    # Cancelled Rides: detectar se rec[5] é telefone e extrair endereços adequadamente
                    endereco_completo = None
                    cidade_rec = None
                    estado = None
                    motivo = None

                    # Detectar se rec[5] é telefone (mesma lógica do endpoint de métricas)
                    telefone_detectado = False
                    maybe_5 = str(rec[5]).strip() if len(rec) > 5 and rec[5] is not None else ""
                    if maybe_5 and re.match(r"^\+?\d{7,}$", maybe_5.replace(' ', '').replace('-', '')):
                        telefone_detectado = True
                        # Se rec[5] é telefone, buscar endereço em 8/9/6 (mesma lógica do endpoint de métricas)
                        if len(rec) > 8 and rec[8] and is_valid_address(str(rec[8])):
                            endereco_completo = str(rec[8]).strip()
                        elif len(rec) > 9 and rec[9] and is_valid_address(str(rec[9])):
                            endereco_completo = str(rec[9]).strip()
                        elif len(rec) > 6 and rec[6] and is_valid_address(str(rec[6])):
                            endereco_completo = str(rec[6]).strip()
                    else:
                        # Se rec[5] NÃO é telefone, usar rec[5] e rec[6] como endereços (padrão)
                        if len(rec) > 6 and rec[6] and is_valid_address(str(rec[6])):
                            endereco_completo = str(rec[6]).strip()
                        elif len(rec) > 5 and rec[5] and is_valid_address(str(rec[5])):
                            endereco_completo = str(rec[5]).strip()

                    # Se encontrou endereço, tentar extrair cidade e estado
                    if endereco_completo:
                        endereco_completo, cidade_rec, estado = parse_address_components(endereco_completo)

                    # Tentar extrair motivo do cancelamento
                    if len(rec) > 13 and rec[13] and str(rec[13]).strip():
                        motivo = str(rec[13]).strip()

                    # Aplicar filtro de cidade se especificado
                    if cidade and endereco_completo and cidade.lower() not in endereco_completo.lower():
                        continue

                    # Só adicionar se tiver endereço válido
                    if endereco_completo:
                        pontos.append({
                            "endereco": endereco_completo,
                            "cidade": cidade_rec,
                            "estado": estado,
                            "motivo": motivo,
                            "status": "cancelada",
                            "data": dt_corrida.isoformat() if dt_corrida else None
                        })
                        ids_processados.add(id_corrida)

            elif table_name in ["Missed Rides", "corridas_perdidas"]:
                for rec in new_records:
                    total_registros += 1

                    # Extrair ID único para deduplicação
                    id_corrida = rec[0] if len(rec) > 0 else None
                    
                    # DEDUPLICAÇÃO: Pular se ID já foi processado
                    if id_corrida in ids_processados:
                        continue

                    # Tentar extrair data
                    dt_corrida = None
                    if len(rec) > 6 and rec[6]:
                        dt_str = extract_datetime_from_record([rec[6]], 0)
                        if dt_str:
                            try:
                                dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                            except Exception:
                                pass

                    # Aplicar filtro temporal
                    if dt_corrida and not (dt_ini <= dt_corrida <= dt_fim):
                        continue

                    # CORREÇÃO: Usar os MESMOS índices do endpoint de métricas
                    # Missed Rides: usar rec[3] como endereço (consistente com endpoint de métricas)
                    endereco_completo = None
                    cidade_rec = None
                    estado = None

                    if len(rec) > 3 and rec[3] and is_valid_address(str(rec[3])):
                        endereco_completo = str(rec[3]).strip()

                    # Se encontrou endereço, tentar extrair cidade e estado
                    if endereco_completo:
                        endereco_completo, cidade_rec, estado = parse_address_components(endereco_completo)

                    # Fallback: tentar cidade do índice [8] se disponível
                    if not cidade_rec and len(rec) > 8 and rec[8] and str(rec[8]).strip():
                        cidade_rec = str(rec[8]).strip()

                    # Aplicar filtro de cidade se especificado
                    if cidade and endereco_completo and cidade.lower() not in endereco_completo.lower():
                        continue

                    # Só adicionar se tiver endereço válido
                    if endereco_completo:
                        pontos.append({
                            "endereco": endereco_completo,
                            "cidade": cidade_rec,
                            "estado": estado,
                            "status": "perdida",
                            "data": dt_corrida.isoformat() if dt_corrida else None
                        })
                        ids_processados.add(id_corrida)

            elif table_name in ["Completed Rides", "corridas_concluidas"]:
                for rec in new_records:
                    total_registros += 1

                    # Extrair ID único para deduplicação
                    id_corrida = rec[0] if len(rec) > 0 else None
                    
                    # DEDUPLICAÇÃO: Pular se ID já foi processado
                    if id_corrida in ids_processados:
                        continue

                    # Tentar extrair data
                    dt_corrida = None
                    for idx in [7, 8, 6]:  # Possíveis índices de data
                        if idx < len(rec) and rec[idx]:
                            dt_str = extract_datetime_from_record([rec[idx]], 0)
                            if dt_str:
                                try:
                                    dt_corrida = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                    break
                                except Exception:
                                    continue

                    # Aplicar filtro temporal
                    if dt_corrida and not (dt_ini <= dt_corrida <= dt_fim):
                        continue

                    # CORREÇÃO: Usar os MESMOS índices do endpoint de métricas
                    # Completed Rides: usar rec[5] (local) e rec[6] (destino) como no endpoint de métricas
                    endereco_completo = None
                    cidade_rec = None
                    estado = None

                    # Tentar extrair endereço dos índices [5] e [6] (como no endpoint de métricas)
                    if len(rec) > 6 and rec[6] and is_valid_address(str(rec[6])):
                        endereco_completo = str(rec[6]).strip()
                    elif len(rec) > 5 and rec[5] and is_valid_address(str(rec[5])):
                        endereco_completo = str(rec[5]).strip()

                    # Se encontrou endereço, tentar extrair cidade e estado
                    if endereco_completo:
                        endereco_completo, cidade_rec, estado = parse_address_components(endereco_completo)

                    # Fallback: tentar cidade do índice [15] se disponível
                    if not cidade_rec and len(rec) > 15 and rec[15] and str(rec[15]).strip():
                        cidade_rec = str(rec[15]).strip()

                    # Aplicar filtro de cidade se especificado
                    if cidade and cidade_rec and cidade.lower() not in cidade_rec.lower():
                        continue

                    # Só adicionar se tiver endereço válido
                    if endereco_completo:
                        pontos.append({
                            "endereco": endereco_completo,
                            "cidade": cidade_rec,
                            "estado": estado,
                            "status": "concluida",
                            "data": dt_corrida.isoformat() if dt_corrida else None
                        })
                        ids_processados.add(id_corrida)

        # Estatísticas dos dados
        stats = {
            "total_registros_processados": total_registros,
            "pontos_geocodificados": len(pontos),
            "ids_unicos_processados": len(ids_processados),
            "duplicatas_removidas": total_registros - len(ids_processados),
            "periodo": periodo,
            "cidade_filtro": cidade,
            "data_inicio": dt_ini.isoformat(),
            "data_fim": dt_fim.isoformat()
        }

        return {
            "pontos": pontos,
            "estatisticas": stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar dados do mapa de calor: {str(e)}"
        )
