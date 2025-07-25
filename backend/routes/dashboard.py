from flask import Blueprint, jsonify, request
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from src.services.google_sheets_service import GoogleSheetsService
dashboard_bp = Blueprint('dashboard', __name__)
CORS(dashboard_bp)
# Instância do serviço Google Sheets
sheets_service = GoogleSheetsService()

@dashboard_bp.route('/metrics/overview', methods=['GET'])
def get_metrics_overview():
    """Retorna métricas gerais do dashboard"""
    try:
        # Buscar dados das planilhas
        corridas_concluidas = sheets_service.get_corridas_concluidas()
        corridas_canceladas = sheets_service.get_corridas_canceladas()
        corridas_perdidas = sheets_service.get_corridas_perdidas()
        
        # Calcular métricas
        total_corridas = len(corridas_concluidas) + len(corridas_canceladas) + len(corridas_perdidas)
        
        if total_corridas == 0:
            return jsonify({
                'total_corridas': 0,
                'corridas_concluidas': {'total': 0, 'percentual': 0},
                'corridas_canceladas': {'total': 0, 'percentual': 0},
                'corridas_perdidas': {'total': 0, 'percentual': 0}
            })
        
        metrics = {
            'total_corridas': total_corridas,
            'corridas_concluidas': {
                'total': len(corridas_concluidas),
                'percentual': round((len(corridas_concluidas) / total_corridas) * 100, 2)
            },
            'corridas_canceladas': {
                'total': len(corridas_canceladas),
                'percentual': round((len(corridas_canceladas) / total_corridas) * 100, 2)
            },
            'corridas_perdidas': {
                'total': len(corridas_perdidas),
                'percentual': round((len(corridas_perdidas) / total_corridas) * 100, 2)
            }
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/metrics/metas-cidades', methods=['GET'])
def get_metas_cidades():
    """Retorna dados de metas por cidade"""
    try:
        metas = sheets_service.get_metas()
        corridas_concluidas = sheets_service.get_corridas_concluidas()
        
        # Processar dados por cidade
        cidades_data = []
        
        for meta in metas:
            cidade = meta.get('Cidade', '')
            meta_mes_atual = meta.get('Meta Mês 1', 0)  # Assumindo mês atual como Mês 1
            
            # Contar corridas concluídas por cidade no mês atual
            corridas_cidade = [c for c in corridas_concluidas if c.get('Municipio', '') == cidade]
            realizado = len(corridas_cidade)
            
            # Calcular percentual
            percentual = (realizado / meta_mes_atual * 100) if meta_mes_atual > 0 else 0
            
            # Definir status baseado no percentual
            if percentual >= 100:
                status = 'success'
            elif percentual >= 80:
                status = 'warning'
            else:
                status = 'danger'
            
            cidades_data.append({
                'cidade': cidade,
                'meta': meta_mes_atual,
                'realizado': realizado,
                'percentual': round(percentual, 2),
                'status': status
            })
        
        return jsonify(cidades_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/metrics/analise-corridas', methods=['GET'])
def get_analise_corridas():
    """Retorna dados para análise de corridas (gráficos de pizza)"""
    try:
        corridas_canceladas = sheets_service.get_corridas_canceladas()
        corridas_perdidas = sheets_service.get_corridas_perdidas()
        
        # Análise de motivos de cancelamento
        motivos_cancelamento = {}
        for corrida in corridas_canceladas:
            motivo = corrida.get('Motivo - CC', 'Não informado')
            motivos_cancelamento[motivo] = motivos_cancelamento.get(motivo, 0) + 1
        
        # Análise de motivos de perda
        motivos_perda = {}
        for corrida in corridas_perdidas:
            motivo = corrida.get('Motivo - CP', 'Não informado')
            motivos_perda[motivo] = motivos_perda.get(motivo, 0) + 1
        
        return jsonify({
            'motivos_cancelamento': motivos_cancelamento,
            'motivos_perda': motivos_perda
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/metrics/comparativo-temporal', methods=['GET'])
def get_comparativo_temporal():
    """Retorna dados para comparativos temporais"""
    try:
        periodo = request.args.get('periodo', '7dias')  # 7dias, 4semanas, 6meses
        
        corridas_concluidas = sheets_service.get_corridas_concluidas()
        corridas_canceladas = sheets_service.get_corridas_canceladas()
        corridas_perdidas = sheets_service.get_corridas_perdidas()
        
        # Processar dados baseado no período
        if periodo == '7dias':
            data = _processar_ultimos_7_dias(corridas_concluidas, corridas_canceladas, corridas_perdidas)
        elif periodo == '4semanas':
            data = _processar_ultimas_4_semanas(corridas_concluidas, corridas_canceladas, corridas_perdidas)
        elif periodo == '6meses':
            data = _processar_ultimos_6_meses(corridas_concluidas, corridas_canceladas, corridas_perdidas)
        else:
            return jsonify({'error': 'Período inválido'}), 400
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _processar_ultimos_7_dias(concluidas, canceladas, perdidas):
    """Processa dados dos últimos 7 dias"""
    hoje = datetime.now()
    dados = []
    
    for i in range(7):
        data = hoje - timedelta(days=i)
        data_str = data.strftime('%Y-%m-%d')
        
        # Contar corridas por tipo nesta data
        concluidas_dia = len([c for c in concluidas if c.get('Data', '').startswith(data_str)])
        canceladas_dia = len([c for c in canceladas if c.get('Data - CC', '').startswith(data_str)])
        perdidas_dia = len([c for c in perdidas if c.get('Data - CP', '').startswith(data_str)])
        
        dados.append({
            'data': data.strftime('%d/%m'),
            'concluidas': concluidas_dia,
            'canceladas': canceladas_dia,
            'perdidas': perdidas_dia,
            'total': concluidas_dia + canceladas_dia + perdidas_dia
        })
    
    return {'periodo': '7dias', 'dados': list(reversed(dados))}

def _processar_ultimas_4_semanas(concluidas, canceladas, perdidas):
    """Processa dados das últimas 4 semanas"""
    hoje = datetime.now()
    dados = []
    
    for i in range(4):
        inicio_semana = hoje - timedelta(weeks=i+1)
        fim_semana = hoje - timedelta(weeks=i)
        
        # Contar corridas da semana
        concluidas_semana = 0
        canceladas_semana = 0
        perdidas_semana = 0
        
        # Implementar lógica de contagem por semana
        # (simplificado para o exemplo)
        
        dados.append({
            'semana': f'Semana {4-i}',
            'concluidas': concluidas_semana,
            'canceladas': canceladas_semana,
            'perdidas': perdidas_semana,
            'total': concluidas_semana + canceladas_semana + perdidas_semana
        })
    
    return {'periodo': '4semanas', 'dados': dados}

def _processar_ultimos_6_meses(concluidas, canceladas, perdidas):
    """Processa dados dos últimos 6 meses"""
    hoje = datetime.now()
    dados = []
    
    for i in range(6):
        # Calcular mês
        mes = hoje.month - i
        ano = hoje.year
        
        if mes <= 0:
            mes += 12
            ano -= 1
        
        # Implementar lógica de contagem por mês
        # (simplificado para o exemplo)
        
        dados.append({
            'mes': f'{mes:02d}/{ano}',
            'concluidas': 0,
            'canceladas': 0,
            'perdidas': 0,
            'total': 0
        })
    
    return {'periodo': '6meses', 'dados': list(reversed(dados))}

@dashboard_bp.route('/config/sheets', methods=['POST'])
def configure_sheets():
    """Configura as planilhas do Google Sheets"""
    try:
        data = request.get_json()
        spreadsheet_id_corridas = data.get('spreadsheet_id_corridas')
        spreadsheet_id_metas = data.get('spreadsheet_id_metas')
        
        # Salvar configuração
        config = {
            'spreadsheet_id_corridas': spreadsheet_id_corridas,
            'spreadsheet_id_metas': spreadsheet_id_metas
        }
        
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sheets_config.json')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        return jsonify({'message': 'Configuração salva com sucesso'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde"""
    return jsonify({'status': 'ok', 'service': 'dashboard-api'})

