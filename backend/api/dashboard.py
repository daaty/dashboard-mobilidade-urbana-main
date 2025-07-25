from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from backend.models import db, Corrida, Motorista, Meta, MetricaDiaria, StatusCorrida, StatusMotorista
from backend.services.cache_service import cache_service
import logging
logger = logging.getLogger(__name__)

bp = Blueprint('dashboard', __name__)

@bp.route('/overview', methods=['GET'])
def get_overview():
    """Retorna overview geral do dashboard com cache otimizado"""
    try:
        # Parâmetros de filtro
        municipio = request.args.get('municipio')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Criar chave de cache baseada nos parâmetros
        cache_params = {
            'municipio': municipio,
            'start_date': start_date,
            'end_date': end_date
        }
        
        # Tentar recuperar do cache primeiro
        cached_data = cache_service.get_dashboard_overview(cache_params)
        if cached_data:
            logger.info("📊 Overview recuperado do cache")
            return jsonify({
                'success': True,
                'data': cached_data,
                'from_cache': True
            })
        
        logger.info("📊 Gerando overview - cache miss")
        
        # Definir período padrão (todos os dados se não especificado)
        if not start_date:
            # Buscar a data mais antiga das corridas
            primeira_corrida = db.session.query(Corrida).order_by(Corrida.data).first()
            if primeira_corrida:
                start_date = primeira_corrida.data.date()
            else:
                start_date = (datetime.utcnow() - timedelta(days=365)).date()
        else:
            start_date = datetime.fromisoformat(start_date).date()
        
        if not end_date:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.fromisoformat(end_date).date()
        
        # Query base para corridas
        corridas_query = db.session.query(Corrida).filter(
            func.date(Corrida.data).between(start_date, end_date)
        )
        
        if municipio:
            corridas_query = corridas_query.filter(Corrida.municipio == municipio)
        
        # Métricas principais
        total_corridas = corridas_query.count()
        corridas_concluidas = corridas_query.filter(Corrida.status == StatusCorrida.CONCLUIDA).count()
        corridas_canceladas = corridas_query.filter(Corrida.status == StatusCorrida.CANCELADA).count()
        corridas_perdidas = corridas_query.filter(Corrida.status == StatusCorrida.PERDIDA).count()
        
        # Taxa de conversão
        taxa_conversao = 0
        if total_corridas > 0:
            taxa_conversao = (corridas_concluidas / total_corridas) * 100
        
        # Receita total
        receita_total = db.session.query(func.coalesce(func.sum(Corrida.valor), 0)).filter(
            and_(
                func.date(Corrida.data).between(start_date, end_date),
                Corrida.status == StatusCorrida.CONCLUIDA,
                Corrida.municipio == municipio if municipio else True
            )
        ).scalar() or 0
        
        # Receita média por corrida
        receita_media = receita_total / corridas_concluidas if corridas_concluidas > 0 else 0
        
        # Motoristas ativos
        motoristas_ativos = db.session.query(func.count(func.distinct(Corrida.motorista_nome))).filter(
            and_(
                func.date(Corrida.data).between(start_date, end_date),
                Corrida.municipio == municipio if municipio else True
            )
        ).scalar() or 0
        
        # Usuários únicos
        usuarios_unicos = db.session.query(func.count(func.distinct(Corrida.usuario_nome))).filter(
            and_(
                func.date(Corrida.data).between(start_date, end_date),
                Corrida.municipio == municipio if municipio else True
            )
        ).scalar() or 0
        
        # Avaliação média
        avaliacao_media = db.session.query(func.avg(Corrida.avaliacao)).filter(
            and_(
                func.date(Corrida.data).between(start_date, end_date),
                Corrida.status == StatusCorrida.CONCLUIDA,
                Corrida.avaliacao.isnot(None),
                Corrida.municipio == municipio if municipio else True
            )
        ).scalar() or 0
        
        # Comparação com período anterior
        previous_start = start_date - (end_date - start_date + timedelta(days=1))
        previous_end = start_date - timedelta(days=1)
        
        previous_corridas = db.session.query(func.count(Corrida.id)).filter(
            and_(
                func.date(Corrida.data).between(previous_start, previous_end),
                Corrida.municipio == municipio if municipio else True
            )
        ).scalar() or 0
        
        previous_receita = db.session.query(func.coalesce(func.sum(Corrida.valor), 0)).filter(
            and_(
                func.date(Corrida.data).between(previous_start, previous_end),
                Corrida.status == StatusCorrida.CONCLUIDA,
                Corrida.municipio == municipio if municipio else True
            )
        ).scalar() or 0
        
        # Calcular variações percentuais
        variacao_corridas = 0
        if previous_corridas > 0:
            variacao_corridas = ((total_corridas - previous_corridas) / previous_corridas) * 100
        
        variacao_receita = 0
        if previous_receita > 0:
            variacao_receita = ((receita_total - previous_receita) / previous_receita) * 100
        
        # Preparar dados para resposta e cache
        response_data = {
            'periodo': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'municipio': municipio
            },
            'metricas_principais': {
                'total_corridas': total_corridas,
                'corridas_concluidas': corridas_concluidas,
                'corridas_canceladas': corridas_canceladas,
                'corridas_perdidas': corridas_perdidas,
                'taxa_conversao': round(taxa_conversao, 2),
                'receita_total': float(receita_total),
                'receita_media_corrida': round(float(receita_media), 2),
                'motoristas_ativos': motoristas_ativos,
                'usuarios_unicos': usuarios_unicos,
                'avaliacao_media': round(float(avaliacao_media), 2)
            },
            'comparacao_anterior': {
                'variacao_corridas': round(variacao_corridas, 2),
                'variacao_receita': round(variacao_receita, 2)
            }
        }
        
        # Armazenar no cache (5 minutos TTL)
        cache_service.set_dashboard_overview(cache_params, response_data, 300)
        logger.info("📊 Overview armazenado no cache")
        
        return jsonify({
            'success': True,
            'data': response_data,
            'from_cache': False
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar overview: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/municipios', methods=['GET'])
def get_municipios():
    """Retorna lista de municípios disponíveis"""
    try:
        municipios = db.session.query(Corrida.municipio).distinct().order_by(Corrida.municipio).all()
        
        return jsonify({
            'success': True,
            'data': [m[0] for m in municipios if m[0]]
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar municípios: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/metricas-diarias', methods=['GET'])
def get_metricas_diarias():
    """Retorna métricas diárias para gráficos"""
    try:
        municipio = request.args.get('municipio')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Definir período padrão (todos os dados se não especificado)
        if not start_date:
            # Buscar a data mais antiga dos dados
            primeira_metrica = db.session.query(MetricaDiaria).order_by(MetricaDiaria.data).first()
            if primeira_metrica:
                start_date = primeira_metrica.data
            else:
                start_date = (datetime.utcnow() - timedelta(days=365)).date()
        else:
            start_date = datetime.fromisoformat(start_date).date()
        
        if not end_date:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.fromisoformat(end_date).date()
        
        # Query base
        query = db.session.query(MetricaDiaria).filter(
            MetricaDiaria.data.between(start_date, end_date)
        )
        
        if municipio:
            query = query.filter(MetricaDiaria.municipio == municipio)
        
        # Buscar métricas
        metricas = query.order_by(MetricaDiaria.data).all()
        
        # Organizar dados para gráficos
        dados_grafico = []
        for metrica in metricas:
            dados_grafico.append({
                'data': metrica.data.isoformat(),
                'municipio': metrica.municipio,
                'total_corridas': metrica.total_corridas,
                'corridas_concluidas': metrica.corridas_concluidas,
                'corridas_canceladas': metrica.corridas_canceladas,
                'receita_total': float(metrica.receita_total),
                'receita_media_corrida': float(metrica.ticket_medio or 0),
                'taxa_conversao': float(metrica.taxa_conversao),
                'motoristas_ativos': metrica.motoristas_ativos,
                'usuarios_unicos': metrica.usuarios_unicos,
                'avaliacao_media': float(metrica.avaliacao_media)
            })
        
        return jsonify({
            'success': True,
            'data': dados_grafico
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar métricas diárias: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/ranking-municipios', methods=['GET'])
def get_ranking_municipios():
    """Retorna ranking de municípios por performance"""
    try:
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
        
        # Agregar métricas por município
        ranking = db.session.query(
            MetricaDiaria.municipio,
            func.sum(MetricaDiaria.total_corridas).label('total_corridas'),
            func.sum(MetricaDiaria.corridas_concluidas).label('corridas_concluidas'),
            func.sum(MetricaDiaria.receita_total).label('receita_total'),
            func.avg(MetricaDiaria.taxa_conversao).label('taxa_conversao_media'),
            func.avg(MetricaDiaria.avaliacao_media).label('avaliacao_media'),
            func.avg(MetricaDiaria.motoristas_ativos).label('motoristas_ativos_media')
        ).filter(
            MetricaDiaria.data.between(start_date, end_date)
        ).group_by(
            MetricaDiaria.municipio
        ).order_by(
            func.sum(MetricaDiaria.receita_total).desc()
        ).all()
        
        dados_ranking = []
        for i, item in enumerate(ranking, 1):
            dados_ranking.append({
                'posicao': i,
                'municipio': item.municipio,
                'total_corridas': int(item.total_corridas or 0),
                'corridas_concluidas': int(item.corridas_concluidas or 0),
                'receita_total': float(item.receita_total or 0),
                'taxa_conversao_media': round(float(item.taxa_conversao_media or 0), 2),
                'avaliacao_media': round(float(item.avaliacao_media or 0), 2),
                'motoristas_ativos_media': round(float(item.motoristas_ativos_media or 0), 1)
            })
        
        return jsonify({
            'success': True,
            'data': dados_ranking
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar ranking de municípios: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/metas-performance', methods=['GET'])
def get_metas_performance():
    """Retorna performance vs metas"""
    try:
        municipio = request.args.get('municipio')
        mes = request.args.get('mes')
        
        if not mes:
            mes = datetime.utcnow().replace(day=1).date()
        else:
            mes = datetime.fromisoformat(mes).date()
        
        # Query base para metas
        metas_query = db.session.query(Meta).filter(
            func.date_trunc('month', Meta.mes) == mes
        )
        
        if municipio:
            metas_query = metas_query.filter(Meta.municipio == municipio)
        
        metas = metas_query.all()
        
        dados_metas = []
        for meta in metas:
            # Buscar performance real do mês
            start_month = meta.mes.replace(day=1)
            if start_month.month == 12:
                end_month = start_month.replace(year=start_month.year + 1, month=1) - timedelta(days=1)
            else:
                end_month = start_month.replace(month=start_month.month + 1) - timedelta(days=1)
            
            performance = db.session.query(
                func.sum(MetricaDiaria.corridas_concluidas).label('corridas_realizadas'),
                func.sum(MetricaDiaria.receita_total).label('receita_realizada'),
                func.avg(MetricaDiaria.motoristas_ativos).label('motoristas_ativos_media')
            ).filter(
                and_(
                    MetricaDiaria.municipio == meta.municipio,
                    MetricaDiaria.data.between(start_month, end_month)
                )
            ).first()
            
            corridas_realizadas = int(performance.corridas_realizadas or 0)
            receita_realizada = float(performance.receita_realizada or 0)
            motoristas_ativos = int(performance.motoristas_ativos_media or 0)
            
            # Calcular percentuais de atingimento
            perc_corridas = (corridas_realizadas / meta.meta_corridas * 100) if meta.meta_corridas > 0 else 0
            perc_receita = (receita_realizada / meta.meta_receita * 100) if meta.meta_receita else 0
            perc_motoristas = (motoristas_ativos / meta.meta_motoristas * 100) if meta.meta_motoristas else 0
            
            dados_metas.append({
                'municipio': meta.municipio,
                'mes': meta.mes.isoformat(),
                'metas': {
                    'corridas': meta.meta_corridas,
                    'receita': float(meta.meta_receita or 0),
                    'motoristas': meta.meta_motoristas or 0
                },
                'realizado': {
                    'corridas': corridas_realizadas,
                    'receita': receita_realizada,
                    'motoristas': motoristas_ativos
                },
                'percentual_atingimento': {
                    'corridas': round(perc_corridas, 2),
                    'receita': round(perc_receita, 2),
                    'motoristas': round(perc_motoristas, 2)
                }
            })
        
        return jsonify({
            'success': True,
            'data': dados_metas
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar metas e performance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/motoristas-performance', methods=['GET'])
def get_motoristas_performance():
    """Retorna performance dos motoristas"""
    try:
        municipio = request.args.get('municipio')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 20))
        
        # Definir período padrão (últimos 30 dias)
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).date()
        else:
            start_date = datetime.fromisoformat(start_date).date()
        
        if not end_date:
            end_date = datetime.utcnow().date()
        else:
            end_date = datetime.fromisoformat(end_date).date()
        
        # Agregar performance por motorista
        query = db.session.query(
            Corrida.motorista_nome,
            Corrida.municipio,
            func.count(Corrida.id).label('total_corridas'),
            func.sum(func.case([(Corrida.status == StatusCorrida.CONCLUIDA, 1)], else_=0)).label('corridas_concluidas'),
            func.sum(func.case([(Corrida.status == StatusCorrida.CANCELADA, 1)], else_=0)).label('corridas_canceladas'),
            func.coalesce(func.sum(func.case([(Corrida.status == StatusCorrida.CONCLUIDA, Corrida.valor)], else_=0)), 0).label('receita_total'),
            func.coalesce(func.avg(func.case([(Corrida.avaliacao.isnot(None), Corrida.avaliacao)], else_=None)), 0).label('avaliacao_media')
        ).filter(
            func.date(Corrida.data).between(start_date, end_date)
        )
        
        if municipio:
            query = query.filter(Corrida.municipio == municipio)
        
        motoristas_performance = query.group_by(
            Corrida.motorista_nome,
            Corrida.municipio
        ).order_by(
            func.coalesce(func.sum(func.case([(Corrida.status == StatusCorrida.CONCLUIDA, Corrida.valor)], else_=0)), 0).desc()
        ).limit(limit).all()
        
        dados_motoristas = []
        for performance in motoristas_performance:
            taxa_conversao = 0
            if performance.total_corridas > 0:
                taxa_conversao = (performance.corridas_concluidas / performance.total_corridas) * 100
            
            receita_media = 0
            if performance.corridas_concluidas > 0:
                receita_media = performance.receita_total / performance.corridas_concluidas
            
            dados_motoristas.append({
                'nome': performance.motorista_nome,
                'municipio': performance.municipio,
                'total_corridas': performance.total_corridas,
                'corridas_concluidas': performance.corridas_concluidas,
                'corridas_canceladas': performance.corridas_canceladas,
                'taxa_conversao': round(taxa_conversao, 2),
                'receita_total': float(performance.receita_total),
                'receita_media_corrida': round(receita_media, 2),
                'avaliacao_media': round(float(performance.avaliacao_media), 2)
            })
        
        return jsonify({
            'success': True,
            'data': dados_motoristas
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar performance dos motoristas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
