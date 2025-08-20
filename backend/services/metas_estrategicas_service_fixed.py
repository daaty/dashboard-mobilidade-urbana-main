"""
Serviço corrigido para gerenciar metas estratégicas, fases de planejamento e relatórios
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, date

from app.models.metas_progressivas import MetasProgressivas
from app.models.fases_planejamento import FasesPlanejamento
from app.models.cidades_demografia import CidadesDemografia

class MetasEstrategicasService:
    """Serviço para gerenciar metas estratégicas e fases de planejamento"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # === METAS PROGRESSIVAS ===
    
    def listar_metas_por_cidade(self) -> List[Dict[str, Any]]:
        """Lista todas as metas progressivas agrupadas por cidade"""
        try:
            metas = self.db.query(
                MetasProgressivas,
                CidadesDemografia.cidade.label('cidade_nome')
            ).join(
                CidadesDemografia, 
                MetasProgressivas.cidade_id == CidadesDemografia.id
            ).order_by(
                CidadesDemografia.cidade,
                MetasProgressivas.mes
            ).all()
            
            resultado = []
            for meta, cidade_nome in metas:
                resultado.append({
                    'id': meta.id,
                    'cidade_nome': cidade_nome,
                    'cidade_id': meta.cidade_id,
                    'mes': meta.mes,
                    'percentual_publico': meta.percentual_publico,
                    'tipo_meta': meta.tipo_meta,
                    'meta_corridas': meta.meta_corridas,
                    'meta_motoristas': meta.meta_motoristas,
                    'meta_usuarios_ativos': meta.meta_usuarios_ativos,
                    'meta_receita': meta.meta_receita,
                    'status': meta.status,
                    'atingida': meta.atingida,
                    'investimento_previsto': meta.investimento_previsto,
                    'investimento_realizado': meta.investimento_realizado,
                    'created_at': meta.created_at.isoformat() if meta.created_at else None,
                    'updated_at': meta.updated_at.isoformat() if meta.updated_at else None
                })
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao listar metas por cidade: {e}")
            return []
    
    def criar_meta_progressiva(self, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria uma nova meta progressiva"""
        try:
            nova_meta = MetasProgressivas(
                cidade_id=dados['cidade_id'],
                fase_id=dados.get('fase_id'),
                mes=dados['mes'],
                percentual_publico=dados['percentual_publico'],
                tipo_meta=dados['tipo_meta'],
                meta_corridas=dados['meta_corridas'],
                meta_motoristas=dados['meta_motoristas'],
                meta_usuarios_ativos=dados.get('meta_usuarios_ativos', 0),
                meta_receita=dados.get('meta_receita', 0.0),
                investimento_previsto=dados.get('investimento_previsto', 0.0)
            )
            
            self.db.add(nova_meta)
            self.db.commit()
            self.db.refresh(nova_meta)
            
            return {
                'id': nova_meta.id,
                'cidade_id': nova_meta.cidade_id,
                'mes': nova_meta.mes,
                'tipo_meta': nova_meta.tipo_meta,
                'meta_corridas': nova_meta.meta_corridas,
                'meta_motoristas': nova_meta.meta_motoristas,
                'status': nova_meta.status
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar meta progressiva: {e}")
            return None
    
    def atualizar_meta_progressiva(self, meta_id: int, dados: Dict[str, Any]) -> Dict:
        """Atualiza uma meta progressiva existente"""
        try:
            meta = self.db.query(MetasProgressivas).filter(MetasProgressivas.id == meta_id).first()
            if not meta:
                return {'success': False, 'error': 'Meta não encontrada'}
            
            # Atualizar campos permitidos
            campos_permitidos = [
                'percentual_publico', 'tipo_meta', 'meta_corridas', 'meta_motoristas',
                'meta_usuarios_ativos', 'meta_receita', 'status', 'investimento_previsto',
                'resultado_corridas', 'resultado_motoristas', 'resultado_usuarios_ativos',
                'resultado_receita', 'investimento_realizado', 'atingida'
            ]
            
            for campo in campos_permitidos:
                if campo in dados:
                    setattr(meta, campo, dados[campo])
            
            meta.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(meta)
            
            return {
                'success': True,
                'message': 'Meta atualizada com sucesso',
                'meta': {
                    'id': meta.id,
                    'status': meta.status,
                    'updated_at': meta.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao atualizar meta progressiva: {e}")
            return {'success': False, 'error': f'Erro interno: {str(e)}'}
    
    def deletar_meta_progressiva(self, meta_id: int) -> Dict:
        """Deleta uma meta progressiva"""
        try:
            meta = self.db.query(MetasProgressivas).filter(MetasProgressivas.id == meta_id).first()
            if not meta:
                return {'success': False, 'error': 'Meta não encontrada'}
            
            # Salvar dados antes de deletar para retorno
            cidade_nome = meta.cidade.cidade if meta.cidade else "N/A"
            mes = meta.mes
            tipo = meta.tipo_meta
            
            self.db.delete(meta)
            self.db.commit()
            
            return {
                'success': True, 
                'message': 'Meta deletada com sucesso',
                'meta_deletada': {
                    'id': meta_id,
                    'cidade': cidade_nome,
                    'mes': mes,
                    'tipo': tipo
                }
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao deletar meta progressiva: {e}")
            return {'success': False, 'error': str(e)}
    
    # === FASES DE PLANEJAMENTO ===
    
    def listar_fases_planejamento(self) -> List[Dict[str, Any]]:
        """Lista todas as fases de planejamento"""
        try:
            fases = self.db.query(FasesPlanejamento).order_by(FasesPlanejamento.id).all()
            
            resultado = []
            for fase in fases:
                resultado.append({
                    'id': fase.id,
                    'nome': fase.nome,
                    'descricao': fase.descricao,
                    'data_inicio': fase.data_inicio.isoformat() if fase.data_inicio else None,
                    'data_fim': fase.data_fim.isoformat() if fase.data_fim else None,
                    'data_inicio_real': fase.data_inicio_real.isoformat() if fase.data_inicio_real else None,
                    'data_fim_real': fase.data_fim_real.isoformat() if fase.data_fim_real else None,
                    'status': fase.status,
                    'progresso_percentual': fase.progresso_percentual,
                    'orcamento_previsto': fase.orcamento_previsto,
                    'orcamento_empenhado': fase.orcamento_empenhado,
                    'orcamento_pago': fase.orcamento_pago,
                    'orcamento_liquidado': fase.orcamento_liquidado,
                    'meta_cidades': fase.meta_cidades,
                    'meta_motoristas': fase.meta_motoristas,
                    'meta_corridas': fase.meta_corridas,
                    'meta_receita': fase.meta_receita,
                    'prazo_meses': fase.prazo_meses,
                    'resultado_cidades': fase.resultado_cidades,
                    'resultado_motoristas': fase.resultado_motoristas,
                    'resultado_corridas': fase.resultado_corridas,
                    'resultado_receita': fase.resultado_receita,
                    'responsavel': fase.responsavel,
                    'observacoes': fase.observacoes
                })
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao listar fases de planejamento: {e}")
            return []
    
    def criar_fase_planejamento(self, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria uma nova fase de planejamento"""
        try:
            nova_fase = FasesPlanejamento(
                nome=dados['nome'],
                descricao=dados.get('descricao'),
                data_inicio=datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date(),
                data_fim=datetime.strptime(dados['data_fim'], '%Y-%m-%d').date(),
                orcamento_previsto=dados['orcamento_previsto'],
                meta_cidades=dados.get('meta_cidades', 0),
                meta_motoristas=dados.get('meta_motoristas', 0),
                meta_corridas=dados.get('meta_corridas', 0),
                meta_receita=dados.get('meta_receita', 0.0),
                prazo_meses=dados.get('prazo_meses', 1),
                responsavel=dados.get('responsavel')
            )
            
            self.db.add(nova_fase)
            self.db.commit()
            self.db.refresh(nova_fase)
            
            return {
                'id': nova_fase.id,
                'nome': nova_fase.nome,
                'status': nova_fase.status,
                'data_inicio': nova_fase.data_inicio.isoformat(),
                'data_fim': nova_fase.data_fim.isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar fase de planejamento: {e}")
            return None
    
    def atualizar_fase_planejamento(self, fase_id: int, dados: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza uma fase de planejamento existente"""
        try:
            fase = self.db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
            if not fase:
                return None
            
            # Atualizar campos permitidos
            if 'nome' in dados:
                fase.nome = dados['nome']
            if 'descricao' in dados:
                fase.descricao = dados['descricao']
            if 'data_inicio' in dados:
                fase.data_inicio = datetime.strptime(dados['data_inicio'], '%Y-%m-%d').date()
            if 'data_fim' in dados:
                fase.data_fim = datetime.strptime(dados['data_fim'], '%Y-%m-%d').date()
            if 'status' in dados:
                fase.status = dados['status']
            if 'progresso_percentual' in dados:
                fase.progresso_percentual = dados['progresso_percentual']
            if 'orcamento_previsto' in dados:
                fase.orcamento_previsto = dados['orcamento_previsto']
            
            self.db.commit()
            self.db.refresh(fase)
            
            return {
                'id': fase.id,
                'nome': fase.nome,
                'status': fase.status
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao atualizar fase de planejamento: {e}")
            return None
    
    def deletar_fase_planejamento(self, fase_id: int) -> bool:
        """Deleta uma fase de planejamento"""
        try:
            fase = self.db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
            if not fase:
                return False
            
            self.db.delete(fase)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao deletar fase de planejamento: {e}")
            return False
    
    # === RELATÓRIOS E DASHBOARD ===
    
    def gerar_relatorio_por_tipo(self) -> Dict[str, Any]:
        """Gera relatório agrupado por tipo de meta"""
        try:
            relatorio = self.db.query(
                MetasProgressivas.tipo_meta,
                func.count(MetasProgressivas.id).label('total_metas'),
                func.sum(MetasProgressivas.meta_corridas).label('total_corridas'),
                func.sum(MetasProgressivas.meta_motoristas).label('total_motoristas'),
                func.avg(MetasProgressivas.percentual_publico).label('media_percentual')
            ).group_by(MetasProgressivas.tipo_meta).all()
            
            resultado = []
            for item in relatorio:
                resultado.append({
                    'tipo_meta': item.tipo_meta,
                    'total_metas': item.total_metas,
                    'total_corridas': item.total_corridas or 0,
                    'total_motoristas': item.total_motoristas or 0,
                    'media_percentual': float(item.media_percentual or 0)
                })
            
            return {
                'success': True,
                'relatorio': resultado,
                'total_tipos': len(resultado)
            }
            
        except Exception as e:
            print(f"Erro ao gerar relatório por tipo: {e}")
            return {
                'success': False,
                'relatorio': [],
                'total_tipos': 0
            }
    
    def obter_dashboard_resumo(self) -> Dict[str, Any]:
        """Obtém dados para dashboard resumo"""
        try:
            # Contar metas por status
            total_metas = self.db.query(MetasProgressivas).count()
            metas_ativas = self.db.query(MetasProgressivas).filter(MetasProgressivas.status == 'ativa').count()
            metas_atingidas = self.db.query(MetasProgressivas).filter(MetasProgressivas.atingida == True).count()
            
            # Contar fases
            total_fases = self.db.query(FasesPlanejamento).count()
            fases_ativas = self.db.query(FasesPlanejamento).filter(FasesPlanejamento.status == 'em_execucao').count()
            
            # Totais de metas
            totais = self.db.query(
                func.sum(MetasProgressivas.meta_corridas).label('total_corridas'),
                func.sum(MetasProgressivas.meta_motoristas).label('total_motoristas'),
                func.sum(MetasProgressivas.meta_receita).label('total_receita')
            ).first()
            
            return {
                'success': True,
                'resumo': {
                    'total_metas': total_metas,
                    'metas_ativas': metas_ativas,
                    'metas_atingidas': metas_atingidas,
                    'total_fases': total_fases,
                    'fases_ativas': fases_ativas,
                    'total_corridas_meta': totais.total_corridas or 0,
                    'total_motoristas_meta': totais.total_motoristas or 0,
                    'total_receita_meta': float(totais.total_receita or 0)
                }
            }
            
        except Exception as e:
            print(f"Erro ao obter dashboard resumo: {e}")
            return {
                'success': False,
                'resumo': {}
            }
