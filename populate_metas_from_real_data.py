#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Popular metas_progressivas com Dados Reais

Extrai dados de:
- rides_data (corridas completadas, canceladas, perdidas)
- driver_personal_details (motoristas por cidade)
- drivers_data (métricas de performance)
- passenger_personal_details (passageiros por cidade)

E popula:
- metas_progressivas.resultado_* (corridas, receita, motoristas, etc)
"""

import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv('backend/.env.production')

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

# Dicionário de Normalização de Cidades
CITY_NORMALIZATION = {
    'MATUPA': 'Matupá',
    'MATUPÁ': 'Matupá',
    'PEIXOTO': 'Peixoto de Azevedo',
    'PEIXOTO DE AZEVEDO': 'Peixoto de Azevedo',
    'GUARANTA': 'Guarantã do Norte',
    'GUARANTÃ': 'Guarantã do Norte',
    'GUARANTÃ DO NORTE': 'Guarantã do Norte',
    'GUARANTA DO NORTE': 'Guarantã do Norte',
    'NOVA MONTE VERDE': 'Nova Monte Verde',
    'NOVA BANDEIRANTES': 'Nova Bandeirantes',
    'COLIDER': 'Colíder',
    'COLÍDER': 'Colíder',
    'TERRA NOVA DO NORTE': 'Terra Nova do Norte'
}

# Mapeamento de nomes normalizados para IDs de cidades
# TODO: Buscar do banco dinamicamente
CITY_ID_MAP = {
    'Matupá': 3,
    'Peixoto de Azevedo': 6,
    'Guarantã do Norte': 7,
    'Nova Monte Verde': None,  # Verificar ID no banco
    'Nova Bandeirantes': None,
    'Colíder': None,
    'Terra Nova do Norte': None
}

def normalizar_cidade(cidade_raw: str) -> str:
    """
    Normaliza nome da cidade para padrão consistente
    
    Args:
        cidade_raw: Nome da cidade como vem do banco (ex: "MATUPA")
        
    Returns:
        Nome normalizado (ex: "Matupá")
    """
    if not cidade_raw:
        return "NÃO IDENTIFICADA"
    
    cidade_upper = str(cidade_raw).strip().upper()
    
    # Tentar match exato
    if cidade_upper in CITY_NORMALIZATION:
        return CITY_NORMALIZATION[cidade_upper]
    
    # Tentar match parcial
    for key, value in CITY_NORMALIZATION.items():
        if key in cidade_upper or cidade_upper in key:
            return value
    
    # Retornar original se não encontrar
    logger.warning(f"Cidade não mapeada: {cidade_raw}")
    return cidade_raw.strip()


def extrair_cidade_de_json(ride_data: dict, table_name: str) -> Optional[str]:
    """
    Extrai cidade do JSON conforme o tipo de corrida
    
    Índices de cidade por tipo:
    - Completed Rides: [15]
    - Cancelled Rides: [17]
    - Missed Rides: [8]
    
    Args:
        ride_data: Dicionário JSON parseado
        table_name: Tipo da tabela (ex: "Completed Rides")
        
    Returns:
        Nome da cidade normalizado ou None
    """
    try:
        if 'newRecords' not in ride_data or not ride_data['newRecords']:
            return None
        
        first_record = ride_data['newRecords'][0]
        
        if table_name == 'Completed Rides' and len(first_record) > 15:
            cidade_raw = first_record[15]
        elif table_name == 'Cancelled Rides' and len(first_record) > 17:
            cidade_raw = first_record[17]
        elif table_name == 'Missed Rides' and len(first_record) > 8:
            cidade_raw = first_record[8]
        else:
            # Tentar extrair de pickup_location (índice 4 em Completed, 7 em Cancelled)
            if table_name == 'Completed Rides' and len(first_record) > 4:
                pickup = first_record[4]
                if 'Matupá' in pickup or 'MATUPA' in pickup:
                    return 'Matupá'
                elif 'Peixoto' in pickup or 'PEIXOTO' in pickup:
                    return 'Peixoto de Azevedo'
            return None
        
        return normalizar_cidade(cidade_raw) if cidade_raw else None
        
    except (IndexError, KeyError, TypeError) as e:
        logger.warning(f"Erro ao extrair cidade: {e}")
        return None


def extrair_corridas_por_cidade(
    conn, 
    periodo_meses: int, 
    data_referencia: datetime = None
) -> Dict[str, Dict]:
    """
    Extrai estatísticas de corridas agrupadas por cidade e período
    
    Args:
        conn: Conexão com PostgreSQL
        periodo_meses: Quantidade de meses a considerar (2, 3, 6, 12)
        data_referencia: Data de referência (padrão: hoje)
        
    Returns:
        {
            'Matupá': {
                'corridas_completadas': 150,
                'corridas_canceladas': 10,
                'corridas_perdidas': 5,
                'receita_total': 2500.00,
                'motoristas_unicos': 12,
                'passageiros_unicos': 80
            },
            ...
        }
    """
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    if data_referencia is None:
        data_referencia = datetime.now()
    
    data_inicio = data_referencia - timedelta(days=periodo_meses * 30)
    
    logger.info(f"Extraindo corridas de {data_inicio} até {data_referencia} ({periodo_meses} meses)")
    
    # Query para buscar todas as corridas do período
    cursor.execute("""
        SELECT 
            table_name,
            ride_data,
            scraped_at
        FROM rides_data
        WHERE table_name IN ('Completed Rides', 'Cancelled Rides', 'Missed Rides')
            AND scraped_at >= %s
            AND scraped_at < %s
        ORDER BY scraped_at DESC;
    """, (data_inicio, data_referencia))
    
    rides = cursor.fetchall()
    logger.info(f"Total de registros brutos: {len(rides)}")
    
    # Agregar por cidade
    stats_por_cidade = {}
    
    for ride in rides:
        try:
            ride_json = json.loads(ride['ride_data'])
            cidade = extrair_cidade_de_json(ride_json, ride['table_name'])
            
            if not cidade or cidade == "NÃO IDENTIFICADA":
                continue
            
            # Inicializar cidade se não existe
            if cidade not in stats_por_cidade:
                stats_por_cidade[cidade] = {
                    'corridas_completadas': 0,
                    'corridas_canceladas': 0,
                    'corridas_perdidas': 0,
                    'receita_total': 0.0,
                    'motoristas_unicos': set(),
                    'passageiros_unicos': set()
                }
            
            # Processar cada registro do array
            for record in ride_json.get('newRecords', []):
                if ride['table_name'] == 'Completed Rides':
                    stats_por_cidade[cidade]['corridas_completadas'] += 1
                    
                    # Extrair receita (índice 12)
                    if len(record) > 12:
                        try:
                            fare_value = record[12]
                            # Limpar string e converter - FILTRAR 'nan', '-', vazios
                            if fare_value:
                                fare_str = str(fare_value).strip().lower()
                                if fare_str and fare_str not in ('nan', '-', '', 'null', 'none'):
                                    receita = float(fare_str.replace(',', '.'))
                                    if receita > 0:  # Só somar valores positivos
                                        stats_por_cidade[cidade]['receita_total'] += receita
                        except (ValueError, TypeError) as e:
                            logger.debug(f"Valor de fare inválido para {cidade}: {record[12]} - {e}")
                    
                    # Motorista (índice 1)
                    if len(record) > 1 and record[1]:
                        stats_por_cidade[cidade]['motoristas_unicos'].add(str(record[1]))
                    
                    # Passageiro (índice 2)
                    if len(record) > 2 and record[2]:
                        stats_por_cidade[cidade]['passageiros_unicos'].add(str(record[2]))
                
                elif ride['table_name'] == 'Cancelled Rides':
                    stats_por_cidade[cidade]['corridas_canceladas'] += 1
                    
                    # Motorista (índice 2 em Cancelled)
                    if len(record) > 2 and record[2]:
                        stats_por_cidade[cidade]['motoristas_unicos'].add(str(record[2]))
                
                elif ride['table_name'] == 'Missed Rides':
                    stats_por_cidade[cidade]['corridas_perdidas'] += 1
        
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Erro ao processar ride: {e}")
            continue
    
    # Converter sets para contadores
    resultado = {}
    for cidade, stats in stats_por_cidade.items():
        resultado[cidade] = {
            'corridas_completadas': stats['corridas_completadas'],
            'corridas_canceladas': stats['corridas_canceladas'],
            'corridas_perdidas': stats['corridas_perdidas'],
            'receita_total': round(stats['receita_total'], 2),
            'motoristas_unicos': len(stats['motoristas_unicos']),
            'passageiros_unicos': len(stats['passageiros_unicos']),
            'total_corridas': (
                stats['corridas_completadas'] + 
                stats['corridas_canceladas'] + 
                stats['corridas_perdidas']
            )
        }
    
    cursor.close()
    return resultado


def contar_motoristas_ativos_por_cidade(
    conn,
    periodo_meses: int,
    data_referencia: datetime = None
) -> Dict[str, int]:
    """
    Conta motoristas que fizeram pelo menos 1 corrida no período
    
    Args:
        conn: Conexão PostgreSQL
        periodo_meses: Período em meses
        data_referencia: Data de referência
        
    Returns:
        {'Matupá': 12, 'Peixoto de Azevedo': 8, ...}
    """
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    if data_referencia is None:
        data_referencia = datetime.now()
    
    data_inicio = data_referencia - timedelta(days=periodo_meses * 30)
    
    # Query para motoristas com corridas recentes
    cursor.execute("""
        SELECT 
            city,
            driver_id,
            rides_history
        FROM driver_personal_details
        WHERE city IS NOT NULL
            AND rides_history IS NOT NULL;
    """)
    
    motoristas = cursor.fetchall()
    
    motoristas_ativos = {}
    
    for motorista in motoristas:
        cidade = normalizar_cidade(motorista['city'])
        
        if cidade == "NÃO IDENTIFICADA":
            continue
        
        # Verificar se tem corridas no período
        try:
            rides_history = motorista['rides_history']
            if not rides_history:
                continue
            
            tem_corrida_recente = False
            for ride in rides_history:
                if 'drop_time' in ride:
                    # Formato: "08/10/2025 : 7:51 pm"
                    try:
                        drop_time_str = ride['drop_time'].replace(':', '').strip()
                        # Simplificar: considerar apenas corridas de 2025
                        if '2025' in drop_time_str:
                            tem_corrida_recente = True
                            break
                    except:
                        pass
            
            if tem_corrida_recente:
                if cidade not in motoristas_ativos:
                    motoristas_ativos[cidade] = set()
                motoristas_ativos[cidade].add(motorista['driver_id'])
        
        except Exception as e:
            logger.warning(f"Erro ao processar motorista {motorista['driver_id']}: {e}")
            continue
    
    # Converter sets para contadores
    resultado = {
        cidade: len(drivers) 
        for cidade, drivers in motoristas_ativos.items()
    }
    
    cursor.close()
    return resultado


def calcular_metricas_performance(
    conn,
    cidade: str,
    periodo_meses: int
) -> Dict[str, float]:
    """
    Calcula métricas de performance (aceitação, avaliação média)
    
    Args:
        conn: Conexão PostgreSQL
        cidade: Nome da cidade normalizado
        periodo_meses: Período em meses
        
    Returns:
        {
            'taxa_aceitacao': 85.5,
            'avaliacao_media': 4.7,
            'taxa_cancelamento_motorista': 5.2
        }
    """
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    # Buscar motoristas da cidade
    cursor.execute("""
        SELECT driver_id
        FROM driver_personal_details
        WHERE city = %s OR UPPER(city) = UPPER(%s);
    """, (cidade, cidade))
    
    driver_ids = [row['driver_id'] for row in cursor.fetchall()]
    
    if not driver_ids:
        return {
            'taxa_aceitacao': 0.0,
            'avaliacao_media': 0.0,
            'taxa_cancelamento_motorista': 0.0
        }
    
    # Buscar métricas de performance
    cursor.execute("""
        SELECT 
            additional_data
        FROM drivers_data
        WHERE driver_id = ANY(%s)
            AND data_type = 'performance'
        ORDER BY scraped_at DESC;
    """, (driver_ids,))
    
    performance_records = cursor.fetchall()
    
    total_success = 0
    total_requests = 0
    total_driver_cancelled = 0
    avaliacoes = []
    
    for record in performance_records:
        try:
            data = record['additional_data']
            
            success_rides = int(data.get('Success Rides', 0))
            requests_received = int(data.get('Requests Received', 0))
            driver_cancelled = int(data.get('Driver Cancelled Rides', 0))
            
            total_success += success_rides
            total_requests += requests_received
            total_driver_cancelled += driver_cancelled
            
        except (ValueError, TypeError, KeyError) as e:
            continue
    
    # Buscar avaliações de rides_history
    cursor.execute("""
        SELECT rides_history
        FROM driver_personal_details
        WHERE driver_id = ANY(%s)
            AND rides_history IS NOT NULL;
    """, (driver_ids,))
    
    for row in cursor.fetchall():
        try:
            rides = row['rides_history']
            for ride in rides:
                if 'driver_rating' in ride and ride['driver_rating'] not in ['--', None]:
                    rating_str = ride['driver_rating'].replace('/5', '').strip()
                    try:
                        rating = float(rating_str)
                        avaliacoes.append(rating)
                    except ValueError:
                        pass
        except:
            continue
    
    # Calcular métricas
    taxa_aceitacao = (total_success / total_requests * 100) if total_requests > 0 else 0
    avaliacao_media = (sum(avaliacoes) / len(avaliacoes)) if avaliacoes else 0
    taxa_cancelamento = (total_driver_cancelled / total_requests * 100) if total_requests > 0 else 0
    
    cursor.close()
    
    return {
        'taxa_aceitacao': round(taxa_aceitacao, 2),
        'avaliacao_media': round(avaliacao_media, 2),
        'taxa_cancelamento_motorista': round(taxa_cancelamento, 2)
    }


def popular_metas_progressivas(
    conn,
    cidade: str,
    cidade_id: int,
    periodo_meses: int,
    stats_corridas: Dict,
    stats_motoristas: int,
    metricas_performance: Dict
):
    """
    Atualiza tabela metas_progressivas com dados reais
    
    Args:
        conn: Conexão PostgreSQL
        cidade: Nome da cidade
        cidade_id: ID da cidade na tabela
        periodo_meses: Período (2, 3, 6, 12)
        stats_corridas: Estatísticas de corridas
        stats_motoristas: Contagem de motoristas ativos
        metricas_performance: Métricas de performance
    """
    cursor = conn.cursor()
    
    logger.info(f"Atualizando metas para {cidade} ({periodo_meses} meses)")
    
    # Verificar se registro existe
    cursor.execute("""
        SELECT id FROM metas_progressivas
        WHERE cidade_id = %s AND mes = %s;
    """, (cidade_id, periodo_meses))
    
    meta_exists = cursor.fetchone()
    
    if not meta_exists:
        logger.warning(f"Meta não encontrada para cidade_id={cidade_id}, mes={periodo_meses}")
        cursor.close()
        return
    
    # Atualizar campos resultado_*
    cursor.execute("""
        UPDATE metas_progressivas
        SET 
            resultado_corridas = %s,
            resultado_receita = %s,
            resultado_motoristas = %s,
            resultado_usuarios_ativos = %s,
            resultado_satisfacao = %s,
            resultado_taxa_cancelamento = %s,
            updated_at = NOW()
        WHERE cidade_id = %s AND mes = %s;
    """, (
        stats_corridas.get('corridas_completadas', 0),
        stats_corridas.get('receita_total', 0),
        stats_motoristas,
        stats_corridas.get('passageiros_unicos', 0),
        metricas_performance.get('avaliacao_media', 0),
        metricas_performance.get('taxa_cancelamento_motorista', 0),
        cidade_id,
        periodo_meses
    ))
    
    conn.commit()
    cursor.close()
    
    logger.info(f"✅ Atualizado: {cursor.rowcount} registro(s)")


def main():
    """Função principal de execução"""
    logger.info("="*80)
    logger.info("🚀 INICIANDO POPULAÇÃO DE METAS COM DADOS REAIS")
    logger.info("="*80)
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info(f"✅ Conectado ao banco: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        
        # Períodos a processar
        periodos = [2, 3, 6, 12]
        
        for periodo in periodos:
            logger.info(f"\n{'='*80}")
            logger.info(f"📊 PROCESSANDO PERÍODO: {periodo} meses")
            logger.info(f"{'='*80}\n")
            
            # 1. Extrair corridas
            logger.info("📍 Extraindo corridas por cidade...")
            stats_corridas = extrair_corridas_por_cidade(conn, periodo)
            
            for cidade, stats in stats_corridas.items():
                logger.info(f"  {cidade}:")
                logger.info(f"    - Completadas: {stats['corridas_completadas']}")
                logger.info(f"    - Canceladas: {stats['corridas_canceladas']}")
                logger.info(f"    - Perdidas: {stats['corridas_perdidas']}")
                logger.info(f"    - Receita: R$ {stats['receita_total']:.2f}")
                logger.info(f"    - Motoristas: {stats['motoristas_unicos']}")
                logger.info(f"    - Passageiros: {stats['passageiros_unicos']}")
            
            # 2. Contar motoristas ativos
            logger.info("\n👨‍✈️ Contando motoristas ativos...")
            stats_motoristas = contar_motoristas_ativos_por_cidade(conn, periodo)
            
            for cidade, count in stats_motoristas.items():
                logger.info(f"  {cidade}: {count} motoristas")
            
            # 3. Popular banco para cada cidade
            logger.info("\n💾 Atualizando metas_progressivas...")
            
            for cidade in stats_corridas.keys():
                cidade_id = CITY_ID_MAP.get(cidade)
                
                if cidade_id is None:
                    logger.warning(f"⚠️ Cidade {cidade} sem ID mapeado, pulando...")
                    continue
                
                # Calcular métricas de performance
                metricas = calcular_metricas_performance(conn, cidade, periodo)
                
                # Popular banco
                popular_metas_progressivas(
                    conn,
                    cidade,
                    cidade_id,
                    periodo,
                    stats_corridas[cidade],
                    stats_motoristas.get(cidade, 0),
                    metricas
                )
        
        conn.close()
        
        logger.info("\n" + "="*80)
        logger.info("✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
