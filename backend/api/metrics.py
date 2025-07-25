from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, and_, text
from backend.models import db, Corrida, Motorista, Meta, MetricaDiaria, StatusCorrida
import logging
logger = logging.getLogger(__name__)
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# Endpoint compatível com frontend React
@router.get("/overview")
async def metrics_overview():
    # Simulação de dados, ajuste conforme necessário
    data = {
        "total_corridas": 1234,
        "corridas_concluidas": 1200,
        "corridas_canceladas": 34,
        "receita_total": 50000.0,
        "ticket_medio": 40.3,
        "taxa_conclusao_media": 97.2,
        "avaliacao_media": 4.8,
        "motoristas_ativos_media": 85
    }
    return JSONResponse(content={"success": True, "data": data})
bp = Blueprint('metrics', __name__)

@bp.route('/kpis', methods=['GET'])
def get_kpis():
    """Retorna KPIs principais"""
    try:
        municipio = request.args.get('municipio')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Definir período padrão (últimos 30 dias)
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).date()
        else:
            start_date = datetime.fromisoformat(start_date).date()
        
        if not end_date:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.fromisoformat(end_date).date()
        
        # Base query para métricas
        base_query = db.session.query(MetricaDiaria).filter(
            MetricaDiaria.data.between(start_date, end_date)
        )
        
        if municipio:
            base_query = base_query.filter(MetricaDiaria.municipio == municipio)
        
        # Agregar KPIs
        kpis_result = base_query.with_entities(
            func.sum(MetricaDiaria.total_corridas).label('total_corridas'),
            func.sum(MetricaDiaria.corridas_concluidas).label('corridas_concluidas'),
            func.sum(MetricaDiaria.corridas_canceladas).label('corridas_canceladas'),
            func.sum(MetricaDiaria.receita_total).label('receita_total'),
            func.avg(MetricaDiaria.ticket_medio).label('ticket_medio'),
            func.avg(MetricaDiaria.taxa_conclusao).label('taxa_conclusao_media'),
            func.avg(MetricaDiaria.avaliacao_media).label('avaliacao_media'),
            func.avg(MetricaDiaria.motoristas_ativos).label('motoristas_ativos_media')
        ).first()
        
        # Calcular período anterior para comparação
        periodo_dias = (end_date - start_date).days + 1
        previous_start = start_date - timedelta(days=periodo_dias)
        previous_end = start_date - timedelta(days=1)
        
        previous_query = base_query.filter(
            MetricaDiaria.data.between(previous_start, previous_end)
        )
        
        if municipio:
            previous_query = previous_query.filter(MetricaDiaria.municipio == municipio)
        
        previous_result = previous_query.with_entities(
            func.sum(MetricaDiaria.total_corridas).label('total_corridas'),
            func.sum(MetricaDiaria.receita_total).label('receita_total'),
            func.avg(MetricaDiaria.taxa_conversao).label('taxa_conversao_media')
        ).first()
        
        # Calcular variações
        def calcular_variacao(atual, anterior):
            if not anterior or anterior == 0:
                return 0
            return ((atual - anterior) / anterior) * 100
        
        kpis = {
            'total_corridas': {
                'valor': int(kpis_result.total_corridas or 0),
                'variacao': calcular_variacao(
                    kpis_result.total_corridas or 0,
                    previous_result.total_corridas or 0
                )
            },
            'corridas_concluidas': {
                'valor': int(kpis_result.corridas_concluidas or 0),
                'percentual': round((kpis_result.corridas_concluidas or 0) / (kpis_result.total_corridas or 1) * 100, 2)
            },
            'receita_total': {
                'valor': float(kpis_result.receita_total or 0),
                'variacao': calcular_variacao(
                    kpis_result.receita_total or 0,
                    previous_result.receita_total or 0 if previous_result else 0
                )
            },
            'ticket_medio': {
                'valor': round(float(kpis_result.ticket_medio or 0), 2)
            },
            'taxa_conclusao': {
                'valor': round(float(kpis_result.taxa_conclusao_media or 0), 2),
                'variacao': calcular_variacao(
                    kpis_result.taxa_conclusao_media or 0,
                    previous_result.taxa_conclusao_media or 0 if previous_result else 0
                )
            },
            'avaliacao_media': {
                'valor': round(float(kpis_result.avaliacao_media or 0), 2)
            },
            'motoristas_ativos': {
                'valor': round(float(kpis_result.motoristas_ativos_media or 0), 1)
            },
            'usuarios_unicos': {
                'valor': int(kpis_result.usuarios_unicos_total or 0)
            }
        }
        
        return jsonify({
            'success': True,
            'data': {
                'periodo': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'municipio': municipio
                },
                'kpis': kpis
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar KPIs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/tendencias', methods=['GET'])
def get_tendencias():
    """Retorna análise de tendências"""
    try:
        municipio = request.args.get('municipio')
        periodo = request.args.get('periodo', '30')  # dias
        
        # Definir período
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=int(periodo))
        
        # Query base
        query = db.session.query(MetricaDiaria).filter(
            MetricaDiaria.data.between(start_date, end_date)
        )
        
        if municipio:
            query = query.filter(MetricaDiaria.municipio == municipio)
        
        # Dados diários para análise de tendência
        dados_diarios = query.order_by(MetricaDiaria.data).all()
        
        # Calcular tendências usando regressão linear simples
        def calcular_tendencia(valores):
            if len(valores) < 2:
                return 0
            
            n = len(valores)
            x = list(range(n))
            y = valores
            
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(xi ** 2 for xi in x)
            
            if n * sum_x2 - sum_x ** 2 == 0:
                return 0
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            return slope
        
        # Extrair valores para análise
        corridas_valores = [d.total_corridas for d in dados_diarios]
        receita_valores = [float(d.receita_total) for d in dados_diarios]
        conversao_valores = [float(d.taxa_conversao) for d in dados_diarios]
        
        tendencias = {
            'corridas': {
                'tendencia': calcular_tendencia(corridas_valores),
                'dados': corridas_valores[-7:] if len(corridas_valores) >= 7 else corridas_valores
            },
            'receita': {
                'tendencia': calcular_tendencia(receita_valores),
                'dados': receita_valores[-7:] if len(receita_valores) >= 7 else receita_valores
            },
            'taxa_conversao': {
                'tendencia': calcular_tendencia(conversao_valores),
                'dados': conversao_valores[-7:] if len(conversao_valores) >= 7 else conversao_valores
            }
        }
        
        # Classificar tendências
        for key in tendencias:
            tend = tendencias[key]['tendencia']
            if tend > 0.1:
                tendencias[key]['classificacao'] = 'crescente'
            elif tend < -0.1:
                tendencias[key]['classificacao'] = 'decrescente'
            else:
                tendencias[key]['classificacao'] = 'estavel'
        
        return jsonify({
            'success': True,
            'data': {
                'periodo_analise': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'dias': int(periodo)
                },
                'tendencias': tendencias
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular tendências: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/comparativo-semanal', methods=['GET'])
def get_comparativo_semanal():
    """Retorna comparativo semanal"""
    try:
        municipio = request.args.get('municipio')
        semanas = int(request.args.get('semanas', 4))
        
        # Calcular semanas
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(weeks=semanas)
        
        # Query com agrupamento por semana
        query = db.session.query(
            func.date_trunc('week', MetricaDiaria.data).label('semana'),
            func.sum(MetricaDiaria.total_corridas).label('total_corridas'),
            func.sum(MetricaDiaria.corridas_concluidas).label('corridas_concluidas'),
            func.sum(MetricaDiaria.receita_total).label('receita_total'),
            func.avg(MetricaDiaria.taxa_conversao).label('taxa_conversao_media'),
            func.avg(MetricaDiaria.avaliacao_media).label('avaliacao_media')
        ).filter(
            MetricaDiaria.data.between(start_date, end_date)
        )
        
        if municipio:
            query = query.filter(MetricaDiaria.municipio == municipio)
        
        dados_semanais = query.group_by(
            func.date_trunc('week', MetricaDiaria.data)
        ).order_by(
            func.date_trunc('week', MetricaDiaria.data)
        ).all()
        
        comparativo = []
        for i, semana in enumerate(dados_semanais):
            comparativo.append({
                'semana': semana.semana.isoformat(),
                'numero_semana': i + 1,
                'total_corridas': int(semana.total_corridas or 0),
                'corridas_concluidas': int(semana.corridas_concluidas or 0),
                'receita_total': float(semana.receita_total or 0),
                'taxa_conversao_media': round(float(semana.taxa_conversao_media or 0), 2),
                'avaliacao_media': round(float(semana.avaliacao_media or 0), 2)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'periodo': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'semanas_analisadas': semanas
                },
                'comparativo_semanal': comparativo
            }
        })
        
    except Exception as e:
        logger.error(f"Erro no comparativo semanal: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/distribuicao-horarios', methods=['GET'])
def get_distribuicao_horarios():
    """Retorna distribuição de corridas por horário"""
    try:
        municipio = request.args.get('municipio')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Definir período padrão (últimos 30 dias)
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).date()
        else:
            start_date = datetime.fromisoformat(start_date).date()
        
        if not end_date:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.fromisoformat(end_date).date()
        
        # Query para distribuição por hora
        query = db.session.query(
            func.extract('hour', Corrida.data).label('hora'),
            func.count(Corrida.id).label('total_corridas'),
            func.sum(func.case([(Corrida.status == StatusCorrida.CONCLUIDA, 1)], else_=0)).label('corridas_concluidas'),
            func.coalesce(func.sum(func.case([(Corrida.status == StatusCorrida.CONCLUIDA, Corrida.valor)], else_=0)), 0).label('receita_total')
        ).filter(
            func.date(Corrida.data).between(start_date, end_date)
        )
        
        if municipio:
            query = query.filter(Corrida.municipio == municipio)
        
        distribuicao_horaria = query.group_by(
            func.extract('hour', Corrida.data)
        ).order_by(
            func.extract('hour', Corrida.data)
        ).all()
        
        dados_horarios = []
        for hora_data in distribuicao_horaria:
            hora = int(hora_data.hora)
            taxa_conversao = 0
            if hora_data.total_corridas > 0:
                taxa_conversao = (hora_data.corridas_concluidas / hora_data.total_corridas) * 100
            
            dados_horarios.append({
                'hora': hora,
                'hora_formatada': f"{hora:02d}:00",
                'total_corridas': hora_data.total_corridas,
                'corridas_concluidas': hora_data.corridas_concluidas,
                'receita_total': float(hora_data.receita_total),
                'taxa_conversao': round(taxa_conversao, 2)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'periodo': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'municipio': municipio
                },
                'distribuicao_horarios': dados_horarios
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na distribuição de horários: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/analise-cancelamentos', methods=['GET'])
def get_analise_cancelamentos():
    """Retorna análise de cancelamentos"""
    try:
        municipio = request.args.get('municipio')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Definir período padrão (últimos 30 dias)
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).date()
        else:
            start_date = datetime.fromisoformat(start_date).date()
        
        if not end_date:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.fromisoformat(end_date).date()
        
        # Query base para cancelamentos
        cancelamentos_query = db.session.query(Corrida).filter(
            and_(
                func.date(Corrida.data).between(start_date, end_date),
                Corrida.status == StatusCorrida.CANCELADA
            )
        )
        
        if municipio:
            cancelamentos_query = cancelamentos_query.filter(Corrida.municipio == municipio)
        
        # Análise por motivo de cancelamento
        motivos = db.session.query(
            Corrida.motivo_cancelamento,
            func.count(Corrida.id).label('quantidade')
        ).filter(
            and_(
                func.date(Corrida.data).between(start_date, end_date),
                Corrida.status == StatusCorrida.CANCELADA,
                Corrida.motivo_cancelamento.isnot(None),
                Corrida.municipio == municipio if municipio else True
            )
        ).group_by(
            Corrida.motivo_cancelamento
        ).order_by(
            func.count(Corrida.id).desc()
        ).all()
        
        # Análise por horário
        cancelamentos_por_hora = db.session.query(
            func.extract('hour', Corrida.data).label('hora'),
            func.count(Corrida.id).label('cancelamentos')
        ).filter(
            and_(
                func.date(Corrida.data).between(start_date, end_date),
                Corrida.status == StatusCorrida.CANCELADA,
                Corrida.municipio == municipio if municipio else True
            )
        ).group_by(
            func.extract('hour', Corrida.data)
        ).order_by(
            func.extract('hour', Corrida.data)
        ).all()
        
        # Análise por município (se não filtrado)
        cancelamentos_por_municipio = []
        if not municipio:
            cancelamentos_por_municipio = db.session.query(
                Corrida.municipio,
                func.count(Corrida.id).label('cancelamentos'),
                func.count(Corrida.id) * 100.0 / func.count(Corrida.id).over().label('percentual')
            ).filter(
                and_(
                    func.date(Corrida.data).between(start_date, end_date),
                    Corrida.status == StatusCorrida.CANCELADA
                )
            ).group_by(
                Corrida.municipio
            ).order_by(
                func.count(Corrida.id).desc()
            ).all()
        
        # Total de cancelamentos
        total_cancelamentos = cancelamentos_query.count()
        
        # Total geral de corridas para calcular taxa
        total_corridas = db.session.query(func.count(Corrida.id)).filter(
            and_(
                func.date(Corrida.data).between(start_date, end_date),
                Corrida.municipio == municipio if municipio else True
            )
        ).scalar()
        
        taxa_cancelamento = (total_cancelamentos / total_corridas * 100) if total_corridas > 0 else 0
        
        analise = {
            'resumo': {
                'total_cancelamentos': total_cancelamentos,
                'total_corridas': total_corridas,
                'taxa_cancelamento': round(taxa_cancelamento, 2)
            },
            'motivos': [
                {
                    'motivo': motivo.motivo_cancelamento,
                    'quantidade': motivo.quantidade,
                    'percentual': round((motivo.quantidade / total_cancelamentos * 100), 2) if total_cancelamentos > 0 else 0
                }
                for motivo in motivos
            ],
            'por_horario': [
                {
                    'hora': int(hora.hora),
                    'hora_formatada': f"{int(hora.hora):02d}:00",
                    'cancelamentos': hora.cancelamentos
                }
                for hora in cancelamentos_por_hora
            ],
            'por_municipio': [
                {
                    'municipio': item.municipio,
                    'cancelamentos': item.cancelamentos,
                    'percentual': round(float(item.percentual), 2)
                }
                for item in cancelamentos_por_municipio
            ] if not municipio else []
        }
        
        return jsonify({
            'success': True,
            'data': {
                'periodo': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'municipio': municipio
                },
                'analise_cancelamentos': analise
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na análise de cancelamentos: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/export-dados', methods=['POST'])
def export_dados():
    """Endpoint para exportar dados em formato CSV/Excel"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'csv')  # csv ou excel
        municipio = data.get('municipio')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # TODO: Implementar exportação real
        # Por agora, retornar dados simulados
        
        return jsonify({
            'success': True,
            'data': {
                'download_url': '/api/download/dados-export.csv',
                'filename': f'dados-dashboard-{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.{export_type}',
                'size': '1.2MB',
                'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na exportação de dados: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
