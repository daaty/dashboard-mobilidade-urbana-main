from flask import Blueprint, request, jsonify
from backend.services.sync_service import DataSyncService
import logging
logger = logging.getLogger(__name__)

bp = Blueprint('sync', __name__)

# Inicializar serviço de sincronização
sync_service = DataSyncService()

@bp.route('/execute', methods=['POST'])
def execute_sync():
    """Endpoint para executar sincronização completa"""
    try:
        data = request.get_json() or {}
        force = data.get('force', False)
        
        # Executar sincronização
        result = sync_service.sync_all_data(force=force)
        
        status_code = 200 if result['success'] else 500
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Erro na sincronização: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/google-sheets', methods=['POST'])
def sync_google_sheets():
    """Endpoint para sincronizar apenas Google Sheets"""
    try:
        data = request.get_json() or {}
        force = data.get('force', False)
        
        # Sincronizar apenas Google Sheets
        result = sync_service.sync_from_google_sheets(force=force)
        
        status_code = 200 if result.get('success', True) else 500
        
        return jsonify({
            'success': result.get('success', True),
            'data': result
        }), status_code
        
    except Exception as e:
        logger.error(f"Erro na sincronização do Google Sheets: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/metrics/recalculate', methods=['POST'])
def recalculate_metrics():
    """Endpoint para recalcular métricas diárias"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        
        if start_date:
            from datetime import datetime
            start_date = datetime.fromisoformat(start_date)
        
        # Recalcular métricas
        result = sync_service.recalculate_daily_metrics(start_date=start_date)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Erro no recálculo de métricas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/duplicates/resolve', methods=['POST'])
def resolve_duplicates():
    """Endpoint para resolver duplicatas"""
    try:
        # Resolver duplicatas
        result = sync_service.resolve_duplicates()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Erro na resolução de duplicatas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/status', methods=['GET'])
def get_sync_status():
    """Endpoint para obter status da sincronização"""
    try:
        # Gerar resumo do status atual
        summary = sync_service.generate_sync_summary()
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status de sincronização: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/health', methods=['GET'])
def sync_health_check():
    """Endpoint para verificar saúde do sistema de sincronização"""
    try:
        from backend.models import db, Corrida, MetricaDiaria
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Verificar conectividade com banco
        try:
            corridas_count = db.session.query(func.count(Corrida.id)).scalar()
            db_healthy = True
        except Exception:
            corridas_count = 0
            db_healthy = False
        
        # Verificar métricas recentes
        cutoff_date = (datetime.utcnow() - timedelta(days=1)).date()
        recent_metrics = db.session.query(func.count(MetricaDiaria.id)).filter(
            MetricaDiaria.data >= cutoff_date
        ).scalar()
        
        # Verificar Google Sheets (simulado - implementar verificação real)
        google_sheets_healthy = True  # TODO: Implementar verificação real
        
        health_status = {
            'database': {
                'healthy': db_healthy,
                'total_corridas': corridas_count
            },
            'metrics': {
                'recent_metrics_count': recent_metrics,
                'last_calculation_ok': recent_metrics > 0
            },
            'google_sheets': {
                'healthy': google_sheets_healthy,
                'last_sync': None  # TODO: Implementar tracking de última sincronização
            },
            'overall_healthy': db_healthy and google_sheets_healthy
        }
        
        return jsonify({
            'success': True,
            'data': health_status
        })
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'overall_healthy': False
            }
        }), 500
