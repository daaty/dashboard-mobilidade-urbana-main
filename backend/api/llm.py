#!/usr/bin/env python3
"""
API LLM - Endpoints para Chat Inteligente e Insights
Integração com Google Gemini para análises automáticas
"""
from flask import Blueprint, jsonify, request
from backend.services.llm_service import llm_service
from backend.services.cache_service import cache_service
from backend.api.dashboard import get_overview
import asyncio
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('llm', __name__)

@bp.route('/chat', methods=['POST'])
def chat():
    """Endpoint para chat com LLM"""
    try:
        data = request.get_json()
        question = data.get('question') or data.get('message')
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Pergunta é obrigatória'
            }), 400
        
        # Verificar cache primeiro
        cache_key = f"chat:{hash(question)}"
        try:
            cached_response = cache_service.get(cache_key)
        except Exception as e:
            logger.warning(f"Erro ao acessar cache: {e}")
            cached_response = None
        
        if cached_response:
            logger.info(f"Cache hit para chat: {question[:50]}...")
            return jsonify({
                'success': True,
                'response': cached_response,
                'from_cache': True
            })
        
        # Obter dados do dashboard para contexto
        try:
            dashboard_data = get_overview()
        except Exception as e:
            logger.warning(f"Erro ao obter dados do dashboard: {e}")
            dashboard_data = {}
            
        context = {
            'dashboard_data': dashboard_data,
            'question': question
        }
        
        # Usar função síncrona
        try:
            response = llm_service.chat_sync(question, context)
        except Exception as e:
            logger.error(f"Erro no LLM service: {e}")
            response = "Olá! Sou o assistente de IA do dashboard. Como posso ajudá-lo a analisar os dados de mobilidade urbana?"
        
        # Armazenar no cache
        try:
            cache_service.set(cache_key, response, ttl=300)  # 5 minutos
        except Exception as e:
            logger.warning(f"Erro ao salvar no cache: {e}")
        
        return jsonify({
            'success': True,
            'response': response,
            'from_cache': False
        })
        
    except Exception as e:
        logger.error(f"Erro no chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@bp.route('/insights', methods=['GET'])
def get_insights():
    """Gera insights automáticos baseados nos dados atuais"""
    try:
        # Verificar cache de insights primeiro
        cached_insights = cache_service.get("dashboard:insights")
        if cached_insights:
            logger.info("🔍 Insights recuperados do cache")
            return jsonify({
                'success': True,
                'data': cached_insights,
                'from_cache': True
            })
        
        # Obter dados do dashboard
        dashboard_data = _get_dashboard_data_for_context()
        
        # Gerar insights com LLM síncrono
        response = llm_service.generate_insights_sync(dashboard_data)
        
        if response['success']:
            # Cache por 15 minutos
            cache_service.set("dashboard:insights", response, 900)
            logger.info("🔍 Insights gerados e armazenados no cache")
        
        return jsonify({
            'success': response['success'],
            'data': response,
            'from_cache': False
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

@bp.route('/report', methods=['POST'])
def generate_report():
    """Gera relatório narrativo automático"""
    try:
        data = request.get_json() or {}
        report_type = data.get('type', 'executive')
        
        # Validar tipo de relatório
        valid_types = ['executive', 'operational', 'financial', 'technical']
        if report_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Tipo de relatório inválido. Use: {", ".join(valid_types)}'
            }), 400
        
        # Verificar cache específico do tipo de relatório
        cache_key = f"dashboard:report:{report_type}"
        cached_report = cache_service.get(cache_key)
        if cached_report:
            logger.info(f"📋 Relatório {report_type} recuperado do cache")
            return jsonify({
                'success': True,
                'data': cached_report,
                'from_cache': True
            })
        
        # Obter dados do dashboard
        dashboard_data = _get_dashboard_data_for_context()
        
        # Gerar relatório com LLM síncrono
        response = llm_service.generate_report_sync(dashboard_data, report_type)
        
        if response['success']:
            # Cache por 30 minutos
            cache_service.set(cache_key, response, 1800)
            logger.info(f"📋 Relatório {report_type} gerado e armazenado no cache")
        
        return jsonify({
            'success': response['success'],
            'data': response,
            'from_cache': False
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'details': str(e)
        }), 500

@bp.route('/clear-cache', methods=['POST'])
def clear_llm_cache():
    """Limpa cache de insights e relatórios LLM"""
    try:
        # Limpar caches específicos do LLM
        insights_cleared = cache_service.delete("dashboard:insights")
        reports_cleared = cache_service.invalidate_pattern("dashboard:report:*")
        
        logger.info(f"🧹 Cache LLM limpo - Insights: {insights_cleared}, Relatórios: {reports_cleared}")
        
        return jsonify({
            'success': True,
            'message': 'Cache LLM limpo com sucesso',
            'cleared': {
                'insights': insights_cleared,
                'reports': reports_cleared
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache LLM: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

@bp.route('/status', methods=['GET'])
def get_llm_status():
    """Status do serviço LLM e estatísticas"""
    try:
        # Status do LLM
        llm_status = {
            'enabled': llm_service.enabled,
            'model': 'gemini-1.5-flash' if llm_service.enabled else 'mock',
            'api_configured': bool(llm_service.api_key) if hasattr(llm_service, 'api_key') else False
        }
        
        # Estatísticas do cache
        cache_stats = cache_service.get_cache_stats()
        
        return jsonify({
            'success': True,
            'llm_service': llm_status,
            'cache_service': cache_stats,
            'features': {
                'chat': True,
                'insights': True,
                'reports': True,
                'cache': True
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status LLM: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

def _get_dashboard_data_for_context():
    """Obtém dados atuais do dashboard para contexto do LLM"""
    try:
        # Tentar usar dados em cache primeiro
        cache_params = {'municipio': None, 'start_date': None, 'end_date': None}
        cached_data = cache_service.get_dashboard_overview(cache_params)
        
        if cached_data:
            logger.info("📊 Dados do dashboard recuperados do cache para LLM")
            return cached_data
        
        # Se não há cache, fazer chamada direta (isso acionará o cache)
        from flask import Flask
        from backend.api.dashboard import get_overview
        
        # Simular request context para a função
        with Flask(__name__).test_request_context():
            overview_response = get_overview()
            if overview_response.status_code == 200:
                response_data = overview_response.get_json()
                return response_data.get('data', {})
        
        logger.warning("⚠️ Não foi possível obter dados do dashboard para LLM")
        return {}
        
    except Exception as e:
        logger.error(f"Erro ao obter dados para contexto LLM: {e}")
        return {}
