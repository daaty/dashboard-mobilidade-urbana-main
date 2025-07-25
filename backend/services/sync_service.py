from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import datetime as dt
from sqlalchemy import func, and_, case
from backend.models import db, Corrida, Motorista, Meta, MetricaDiaria, OrigemDado, StatusCorrida
from backend.services.google_sheets_service import GoogleSheetsService
from backend.services.import_service import ImportService
import logging

logger = logging.getLogger(__name__)

class DataSyncService:
    """Serviço para sincronização de dados entre múltiplas fontes"""
    
    def __init__(self):
        self.google_sheets = GoogleSheetsService()
        self.import_service = ImportService()
        
        # Prioridade das fontes de dados:
        # 1. PostgreSQL (dados internos)
        # 2. Planilhas importadas
        # 3. Google Sheets
        # Prioridade das fontes de dados: PostgreSQL (interno), Importação local, Google Sheets
        self.data_source_priority = [
            OrigemDado.POSTGRES,
            OrigemDado.IMPORT,
            OrigemDado.SHEETS
        ]
    
    def sync_all_data(self, force: bool = False) -> Dict:
        """Sincroniza todos os dados de todas as fontes"""
        sync_results = {
            'started_at': datetime.utcnow(),
            'google_sheets': {},
            'metrics_calculation': {},
            'duplicates_resolution': {},
            'summary': {}
        }
        
        try:
            # 1. Sincronizar do Google Sheets
            logger.info("Iniciando sincronização do Google Sheets")
            sheets_result = self.sync_from_google_sheets(force)
            sync_results['google_sheets'] = sheets_result
            
            # 2. Recalcular métricas
            logger.info("Recalculando métricas diárias")
            metrics_result = self.recalculate_daily_metrics()
            sync_results['metrics_calculation'] = metrics_result
            
            # 3. Resolver duplicatas
            logger.info("Resolvendo duplicatas")
            duplicates_result = self.resolve_duplicates()
            sync_results['duplicates_resolution'] = duplicates_result
            
            # 4. Gerar resumo
            sync_results['summary'] = self.generate_sync_summary()
            sync_results['completed_at'] = datetime.utcnow()
            sync_results['success'] = True
            
            logger.info("Sincronização completa realizada com sucesso")
            
        except Exception as e:
            sync_results['error'] = str(e)
            sync_results['success'] = False
            sync_results['completed_at'] = datetime.utcnow()
            logger.error(f"Erro na sincronização: {e}")
        
        return sync_results
    
    def sync_from_google_sheets(self, force: bool = False) -> Dict:
        """Sincroniza dados do Google Sheets"""
        result = {
            'corridas': {'imported': 0, 'errors': 0},
            'motoristas': {'imported': 0, 'errors': 0},
            'metas': {'imported': 0, 'errors': 0}
        }
        
        try:
            # Verificar se precisa sincronizar
            if not force and not self.should_sync_google_sheets():
                return {
                    'skipped': True,
                    'reason': 'Sincronização não necessária (dados recentes)'
                }
            
            # Sincronizar corridas
            corridas_result = self.google_sheets.get_corridas()
            if corridas_result['success']:
                imported, errors = self.import_google_sheets_corridas(corridas_result['data'])
                result['corridas']['imported'] = imported
                result['corridas']['errors'] = errors
            
            # Sincronizar motoristas
            motoristas_result = self.google_sheets.get_motoristas()
            if motoristas_result['success']:
                imported, errors = self.import_google_sheets_motoristas(motoristas_result['data'])
                result['motoristas']['imported'] = imported
                result['motoristas']['errors'] = errors
            
            # Sincronizar metas
            metas_result = self.google_sheets.get_metas()
            if metas_result['success']:
                imported, errors = self.import_google_sheets_metas(metas_result['data'])
                result['metas']['imported'] = imported
                result['metas']['errors'] = errors
            
            result['success'] = True
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def should_sync_google_sheets(self) -> bool:
        """Verifica se é necessário sincronizar com Google Sheets"""
        # Verificar se existem dados do Google Sheets nos últimos 30 minutos
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        
        recent_data = db.session.query(Corrida).filter(
            and_(
                Corrida.origem_dado == OrigemDado.SHEETS,
                Corrida.data_criacao >= cutoff_time
            )
        ).first()
        
        return recent_data is None
    
    def import_google_sheets_corridas(self, corridas_data: List[Dict]) -> Tuple[int, int]:
        """Importa corridas do Google Sheets"""
        imported = 0
        errors = 0
        
        for corrida_data in corridas_data:
            try:
                # Verificar se já existe (por chave única)
                existing = self.find_existing_corrida(corrida_data)
                
                if existing and existing.origem_dado in [OrigemDado.SYSTEM, OrigemDado.IMPORT]:
                    # Não sobrescrever dados de fontes prioritárias
                    continue
                
                if existing:
                    # Atualizar existente do Google Sheets
                    self.update_corrida_from_dict(existing, corrida_data)
                else:
                    # Criar nova
                    corrida = self.create_corrida_from_dict(corrida_data)
                    corrida.origem_dado = OrigemDado.SHEETS
                    db.session.add(corrida)
                
                imported += 1
                
            except Exception as e:
                errors += 1
                logger.error(f"Erro ao importar corrida: {e}")
        
        db.session.commit()
        return imported, errors
    
    def import_google_sheets_motoristas(self, motoristas_data: List[Dict]) -> Tuple[int, int]:
        """Importa motoristas do Google Sheets"""
        imported = 0
        errors = 0
        
        for motorista_data in motoristas_data:
            try:
                # Verificar se já existe por nome e município
                existing = db.session.query(Motorista).filter(
                    and_(
                        Motorista.nome == motorista_data['nome'],
                        Motorista.municipio == motorista_data['municipio']
                    )
                ).first()
                
                if existing and existing.origem_dado in [OrigemDado.SYSTEM, OrigemDado.IMPORT]:
                    continue
                
                if existing:
                    self.update_motorista_from_dict(existing, motorista_data)
                else:
                    motorista = self.create_motorista_from_dict(motorista_data)
                    motorista.origem_dado = OrigemDado.SHEETS
                    db.session.add(motorista)
                
                imported += 1
                
            except Exception as e:
                errors += 1
                logger.error(f"Erro ao importar motorista: {e}")
        
        db.session.commit()
        return imported, errors
    
    def import_google_sheets_metas(self, metas_data: List[Dict]) -> Tuple[int, int]:
        """Importa metas do Google Sheets"""
        imported = 0
        errors = 0
        
        for meta_data in metas_data:
            try:
                # Verificar se já existe por município e mês
                existing = db.session.query(Meta).filter(
                    and_(
                        Meta.municipio == meta_data['municipio'],
                        Meta.mes == meta_data['mes']
                    )
                ).first()
                
                if existing and existing.origem_dado in [OrigemDado.SYSTEM, OrigemDado.IMPORT]:
                    continue
                
                if existing:
                    self.update_meta_from_dict(existing, meta_data)
                else:
                    meta = self.create_meta_from_dict(meta_data)
                    meta.origem_dado = OrigemDado.SHEETS
                    db.session.add(meta)
                
                imported += 1
                
            except Exception as e:
                errors += 1
                logger.error(f"Erro ao importar meta: {e}")
        
        db.session.commit()
        return imported, errors
    
    def find_existing_corrida(self, corrida_data: Dict) -> Optional[Corrida]:
        """Encontra corrida existente baseada em critérios únicos"""
        # Tentar por combinação de campos únicos
        return db.session.query(Corrida).filter(
            and_(
                Corrida.data == corrida_data['data'],
                Corrida.usuario_nome == corrida_data['usuario_nome'],
                Corrida.motorista_nome == corrida_data['motorista_nome'],
                Corrida.municipio == corrida_data['municipio']
            )
        ).first()
    
    def create_corrida_from_dict(self, data: Dict) -> Corrida:
        """Cria uma Corrida a partir de um dicionário"""
        return Corrida(
            data=data['data'],
            usuario_nome=data['usuario_nome'],
            usuario_telefone=data.get('usuario_telefone'),
            motorista_nome=data['motorista_nome'],
            municipio=data['municipio'],
            valor=data.get('valor'),
            distancia=data.get('distancia'),
            tempo_corrida=data.get('tempo_corrida'),
            status=data.get('status', StatusCorrida.CONCLUIDA),
            avaliacao=data.get('avaliacao'),
            motivo_cancelamento=data.get('motivo_cancelamento')
        )
    
    def update_corrida_from_dict(self, corrida: Corrida, data: Dict):
        """Atualiza uma Corrida existente"""
        corrida.usuario_telefone = data.get('usuario_telefone') or corrida.usuario_telefone
        corrida.valor = data.get('valor') or corrida.valor
        corrida.distancia = data.get('distancia') or corrida.distancia
        corrida.tempo_corrida = data.get('tempo_corrida') or corrida.tempo_corrida
        corrida.status = data.get('status') or corrida.status
        corrida.avaliacao = data.get('avaliacao') or corrida.avaliacao
        corrida.motivo_cancelamento = data.get('motivo_cancelamento') or corrida.motivo_cancelamento
        corrida.data_atualizacao = datetime.utcnow()
    
    def create_motorista_from_dict(self, data: Dict) -> Motorista:
        """Cria um Motorista a partir de um dicionário"""
        return Motorista(
            nome=data['nome'],
            telefone=data.get('telefone'),
            municipio=data['municipio'],
            status=data.get('status'),
            data_cadastro=data.get('data_cadastro')
        )
    
    def update_motorista_from_dict(self, motorista: Motorista, data: Dict):
        """Atualiza um Motorista existente"""
        motorista.telefone = data.get('telefone') or motorista.telefone
        motorista.status = data.get('status') or motorista.status
        motorista.data_atualizacao = datetime.utcnow()
    
    def create_meta_from_dict(self, data: Dict) -> Meta:
        """Cria uma Meta a partir de um dicionário"""
        return Meta(
            municipio=data['municipio'],
            mes=data['mes'],
            meta_corridas=data['meta_corridas'],
            meta_receita=data.get('meta_receita'),
            meta_motoristas=data.get('meta_motoristas')
        )
    
    def update_meta_from_dict(self, meta: Meta, data: Dict):
        """Atualiza uma Meta existente"""
        meta.meta_corridas = data.get('meta_corridas') or meta.meta_corridas
        meta.meta_receita = data.get('meta_receita') or meta.meta_receita
        meta.meta_motoristas = data.get('meta_motoristas') or meta.meta_motoristas
        meta.data_atualizacao = datetime.utcnow()
    
    def recalculate_daily_metrics(self, start_date: Optional[datetime] = None) -> Dict:
        """Recalcula métricas diárias"""
        if start_date is None:
            # Recalcular últimos 30 dias
            start_date = datetime.utcnow() - timedelta(days=30)
        
        # Limpar métricas existentes do período
        db.session.query(MetricaDiaria).filter(
            MetricaDiaria.data >= start_date.date()
        ).delete()
        
        # Buscar corridas por dia e município
        corridas_query = db.session.query(
            func.date(Corrida.data).label('data'),
            Corrida.municipio,
            func.count(Corrida.id).label('total_corridas'),
            func.sum(case((Corrida.status == StatusCorrida.CONCLUIDA, 1), else_=0)).label('corridas_concluidas'),
            func.sum(case((Corrida.status == StatusCorrida.CANCELADA, 1), else_=0)).label('corridas_canceladas'),
            func.sum(case((Corrida.status == StatusCorrida.PERDIDA, 1), else_=0)).label('corridas_perdidas'),
            func.coalesce(func.sum(Corrida.valor), 0).label('receita_total'),
            func.coalesce(func.avg(Corrida.distancia), 0).label('distancia_media'),
            func.coalesce(func.avg(Corrida.tempo_corrida), 0).label('tempo_medio'),
            func.coalesce(func.avg(Corrida.avaliacao), 0).label('avaliacao_media'),
            func.count(func.distinct(Corrida.motorista_nome)).label('motoristas_ativos'),
            func.count(func.distinct(Corrida.usuario_nome)).label('usuarios_unicos')
        ).filter(
            Corrida.data >= start_date
        ).group_by(
            func.date(Corrida.data),
            Corrida.municipio
        ).all()
        
        metrics_created = 0
        
        for corrida_stats in corridas_query:
            # Calcular taxa de conversão
            taxa_conversao = 0
            if corrida_stats.total_corridas > 0:
                taxa_conversao = (corrida_stats.corridas_concluidas / corrida_stats.total_corridas) * 100
            
            # Calcular métricas derivadas
            taxa_conclusao = 0
            if corrida_stats.total_corridas > 0:
                taxa_conclusao = (corrida_stats.corridas_concluidas / corrida_stats.total_corridas) * 100
            
            ticket_medio = 0
            if corrida_stats.corridas_concluidas > 0:
                ticket_medio = corrida_stats.receita_total / corrida_stats.corridas_concluidas
            
            metrica = MetricaDiaria(
                data=corrida_stats.data if isinstance(corrida_stats.data, dt.date) else datetime.strptime(str(corrida_stats.data), '%Y-%m-%d').date(),
                municipio=corrida_stats.municipio,
                total_corridas=corrida_stats.total_corridas,
                corridas_concluidas=corrida_stats.corridas_concluidas,
                corridas_canceladas=corrida_stats.corridas_canceladas,
                corridas_perdidas=corrida_stats.corridas_perdidas,
                receita_total=float(corrida_stats.receita_total),
                distancia_media=float(corrida_stats.distancia_media or 0),
                tempo_medio_corrida=float(corrida_stats.tempo_medio or 0),
                avaliacao_media=float(corrida_stats.avaliacao_media or 0),
                taxa_conclusao=float(taxa_conclusao),
                ticket_medio=float(ticket_medio),
                motoristas_ativos=corrida_stats.motoristas_ativos
            )
            
            db.session.add(metrica)
            metrics_created += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'metrics_created': metrics_created,
            'start_date': start_date.date().isoformat()
        }
    
    def resolve_duplicates(self) -> Dict:
        """Resolve duplicatas baseado na prioridade das fontes"""
        # Encontrar possíveis duplicatas de corridas
        duplicates_query = db.session.query(
            Corrida.data,
            Corrida.usuario_nome,
            Corrida.motorista_nome,
            Corrida.municipio,
            func.count(Corrida.id).label('count')
        ).group_by(
            Corrida.data,
            Corrida.usuario_nome,
            Corrida.motorista_nome,
            Corrida.municipio
        ).having(func.count(Corrida.id) > 1).all()
        
        resolved_count = 0
        
        for dup in duplicates_query:
            # Buscar todas as corridas duplicadas
            duplicates = db.session.query(Corrida).filter(
                Corrida.data == dup.data,
                Corrida.usuario_nome == dup.usuario_nome,
                Corrida.motorista_nome == dup.motorista_nome,
                Corrida.municipio == dup.municipio
            ).order_by(
                case(
                    (Corrida.origem_dado == OrigemDado.SYSTEM, 1),
                    (Corrida.origem_dado == OrigemDado.IMPORT, 2),
                    (Corrida.origem_dado == OrigemDado.SHEETS, 3),
                    else_=4
                ),
                Corrida.data_criacao.desc()
            ).all()

            if len(duplicates) > 1:
                # Manter apenas a primeira (maior prioridade)
                to_keep = duplicates[0]
                to_remove = duplicates[1:]
                
                # Mesclar informações se necessário
                self.merge_corrida_data(to_keep, to_remove)
                
                # Remover duplicatas
                for corrida in to_remove:
                    db.session.delete(corrida)
                
                resolved_count += len(to_remove)
        
        db.session.commit()
        
        return {
            'success': True,
            'duplicates_resolved': resolved_count
        }
    
    def merge_corrida_data(self, master: Corrida, duplicates: List[Corrida]):
        """Mescla dados de corridas duplicadas na master"""
        for dup in duplicates:
            # Preencher campos vazios na master com dados das duplicatas
            if not master.usuario_telefone and dup.usuario_telefone:
                master.usuario_telefone = dup.usuario_telefone
            
            if not master.valor and dup.valor:
                master.valor = dup.valor
            
            if not master.distancia and dup.distancia:
                master.distancia = dup.distancia
            
            if not master.tempo_corrida and dup.tempo_corrida:
                master.tempo_corrida = dup.tempo_corrida
            
            if not master.avaliacao and dup.avaliacao:
                master.avaliacao = dup.avaliacao
            
            if not master.motivo_cancelamento and dup.motivo_cancelamento:
                master.motivo_cancelamento = dup.motivo_cancelamento
    
    def generate_sync_summary(self) -> Dict:
        """Gera resumo da sincronização"""
        # Contar registros por fonte de corridas
        corridas_by_source = db.session.query(
            Corrida.origem_dado,
            func.count(Corrida.id).label('count')
        ).group_by(Corrida.origem_dado).all()
        # Resumo de corridas por fonte
        corridas_summary = {source.value: count for source, count in corridas_by_source}

        # Contar registros por fonte de motoristas (se implementado)
        try:
            motoristas_by_source = db.session.query(
                Motorista.origem_dado,
                func.count(Motorista.id).label('count')
            ).group_by(Motorista.origem_dado).all()
            motoristas_summary = {source.value: count for source, count in motoristas_by_source}
        except AttributeError:
            motoristas_summary = {}

        # Contar registros por fonte de metas (se implementado)
        try:
            metas_by_source = db.session.query(
                Meta.origem_dado,
                func.count(Meta.id).label('count')
            ).group_by(Meta.origem_dado).all()
            metas_summary = {source.value: count for source, count in metas_by_source}
        except AttributeError:
            metas_summary = {}

        # Métricas recentes
        recent_metrics = db.session.query(func.count(MetricaDiaria.id)).filter(
            MetricaDiaria.data >= (datetime.utcnow() - timedelta(days=7)).date()
        ).scalar()

        return {
            'corridas_by_source': corridas_summary,
            'motoristas_by_source': motoristas_summary,
            'metas_by_source': metas_summary,
            'recent_metrics_count': recent_metrics,
            'last_sync_date': datetime.utcnow().isoformat()
        }
