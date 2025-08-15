# 🎯 SERVIÇO DE METAS ESTRATÉGICAS
# Módulo separado para gerenciar metas progressivas e fases de planejamento

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.models.metas_progressivas import MetasProgressivas
from app.models.fases_planejamento import FasesPlanejamento
from app.models.cidades_demografia import CidadesDemografia
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MetasEstrategicasService:
    """Serviço para gerenciar metas estratégicas e fases de planejamento"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== METAS PROGRESSIVAS ==========
    
    def listar_metas_por_cidade(self, cidade_id: Optional[int] = None) -> List[Dict]:
        """Lista metas progressivas organizadas por cidade"""
        try:
            query = self.db.query(MetasProgressivas)
            
            if cidade_id:
                query = query.filter(MetasProgressivas.cidade_id == cidade_id)
            
            metas = query.order_by(MetasProgressivas.cidade_id, MetasProgressivas.mes).all()
            
            # Agrupar por cidade
            metas_por_cidade = {}
            for meta in metas:
                cidade_nome = meta.cidade_nome or f"Cidade {meta.cidade_id}"
                
                if cidade_nome not in metas_por_cidade:
                    metas_por_cidade[cidade_nome] = {
                        'cidade_id': meta.cidade_id,
                        'cidade_nome': cidade_nome,
                        'metas': []
                    }
                
                metas_por_cidade[cidade_nome]['metas'].append({
                    'id': meta.id,
                    'mes': meta.mes,
                    'percentual_penetracao': meta.percentual_penetracao,
                    'meta_corridas': meta.meta_corridas,
                    'meta_motoristas': meta.meta_motoristas,
                    'meta_receita': meta.meta_receita,
                    'tipo_meta': meta.tipo_meta
                })
            
            return list(metas_por_cidade.values())
            
        except Exception as e:
            logger.error(f"Erro ao listar metas por cidade: {e}")
            return []
    
    def criar_meta_progressiva(self, meta_data: Dict) -> Dict:
        """Cria uma nova meta progressiva"""
        try:
            nova_meta = MetasProgressivas(
                cidade_id=meta_data['cidade_id'],
                cidade_nome=meta_data.get('cidade_nome'),
                mes=meta_data['mes'],
                percentual_penetracao=meta_data['percentual_penetracao'],
                meta_corridas=meta_data['meta_corridas'],
                meta_motoristas=meta_data['meta_motoristas'],
                meta_receita=meta_data.get('meta_receita', 0),
                tipo_meta=meta_data.get('tipo_meta', 'media')
            )
            
            self.db.add(nova_meta)
            self.db.commit()
            self.db.refresh(nova_meta)
            
            return {
                'success': True,
                'meta': {
                    'id': nova_meta.id,
                    'cidade_nome': nova_meta.cidade_nome,
                    'mes': nova_meta.mes,
                    'meta_corridas': nova_meta.meta_corridas,
                    'meta_motoristas': nova_meta.meta_motoristas,
                    'tipo_meta': nova_meta.tipo_meta
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar meta progressiva: {e}")
            return {'success': False, 'error': str(e)}
    
    def atualizar_meta_progressiva(self, meta_id: int, meta_data: Dict) -> Dict:
        """Atualiza uma meta progressiva existente"""
        try:
            meta = self.db.query(MetasProgressivas).filter(MetasProgressivas.id == meta_id).first()
            
            if not meta:
                return {'success': False, 'error': 'Meta não encontrada'}
            
            # Atualizar campos
            for campo, valor in meta_data.items():
                if hasattr(meta, campo):
                    setattr(meta, campo, valor)
            
            self.db.commit()
            self.db.refresh(meta)
            
            return {
                'success': True,
                'meta': {
                    'id': meta.id,
                    'cidade_nome': meta.cidade_nome,
                    'mes': meta.mes,
                    'meta_corridas': meta.meta_corridas,
                    'meta_motoristas': meta.meta_motoristas,
                    'tipo_meta': meta.tipo_meta
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar meta progressiva: {e}")
            return {'success': False, 'error': str(e)}
    
    def deletar_meta_progressiva(self, meta_id: int) -> Dict:
        """Deleta uma meta progressiva"""
        try:
            meta = self.db.query(MetasProgressivas).filter(MetasProgressivas.id == meta_id).first()
            
            if not meta:
                return {'success': False, 'error': 'Meta não encontrada'}
            
            self.db.delete(meta)
            self.db.commit()
            
            return {'success': True, 'message': 'Meta deletada com sucesso'}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar meta progressiva: {e}")
            return {'success': False, 'error': str(e)}
    
    def limpar_metas_duplicadas(self) -> Dict:
        """Remove metas duplicadas do sistema"""
        try:
            # Buscar duplicatas baseadas em cidade_id + mes
            duplicatas = self.db.query(MetasProgressivas)\
                .order_by(MetasProgressivas.cidade_id, MetasProgressivas.mes, MetasProgressivas.id)\
                .all()
            
            metas_unicas = {}
            metas_para_deletar = []
            
            for meta in duplicatas:
                chave = f"{meta.cidade_id}_{meta.mes}"
                
                if chave not in metas_unicas:
                    metas_unicas[chave] = meta
                else:
                    # Manter a primeira e marcar as outras para deleção
                    metas_para_deletar.append(meta)
            
            # Deletar duplicatas
            quantidade_deletada = 0
            for meta in metas_para_deletar:
                self.db.delete(meta)
                quantidade_deletada += 1
            
            self.db.commit()
            
            return {
                'success': True,
                'message': f'{quantidade_deletada} metas duplicadas removidas',
                'metas_restantes': len(metas_unicas)
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao limpar metas duplicadas: {e}")
            return {'success': False, 'error': str(e)}
    
    # ========== FASES DE PLANEJAMENTO ==========
    
    def listar_fases_planejamento(self) -> List[Dict]:
        """Lista todas as fases de planejamento"""
        try:
            fases = self.db.query(FasesPlanejamento)\
                .order_by(FasesPlanejamento.ordem, FasesPlanejamento.data_inicio)\
                .all()
            
            return [{
                'id': fase.id,
                'nome': fase.nome,
                'descricao': fase.descricao,
                'data_inicio': fase.data_inicio.isoformat() if fase.data_inicio else None,
                'data_fim': fase.data_fim.isoformat() if fase.data_fim else None,
                'status': fase.status,
                'meta_cidades': fase.meta_cidades,
                'orcamento_previsto': fase.orcamento_previsto,
                'progresso_percentual': fase.progresso_percentual,
                'ordem': fase.ordem
            } for fase in fases]
            
        except Exception as e:
            logger.error(f"Erro ao listar fases de planejamento: {e}")
            return []
    
    def criar_fase_planejamento(self, fase_data: Dict) -> Dict:
        """Cria uma nova fase de planejamento"""
        try:
            nova_fase = FasesPlanejamento(
                nome=fase_data['nome'],
                descricao=fase_data.get('descricao'),
                data_inicio=fase_data.get('data_inicio'),
                data_fim=fase_data.get('data_fim'),
                status=fase_data.get('status', 'planejada'),
                meta_cidades=fase_data.get('meta_cidades', 0),
                orcamento_previsto=fase_data.get('orcamento_previsto', 0),
                progresso_percentual=fase_data.get('progresso_percentual', 0),
                ordem=fase_data.get('ordem', 1)
            )
            
            self.db.add(nova_fase)
            self.db.commit()
            self.db.refresh(nova_fase)
            
            return {
                'success': True,
                'fase': {
                    'id': nova_fase.id,
                    'nome': nova_fase.nome,
                    'status': nova_fase.status,
                    'meta_cidades': nova_fase.meta_cidades,
                    'orcamento_previsto': nova_fase.orcamento_previsto
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar fase de planejamento: {e}")
            return {'success': False, 'error': str(e)}
    
    def atualizar_fase_planejamento(self, fase_id: int, fase_data: Dict) -> Dict:
        """Atualiza uma fase de planejamento existente"""
        try:
            fase = self.db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
            
            if not fase:
                return {'success': False, 'error': 'Fase não encontrada'}
            
            # Atualizar campos
            for campo, valor in fase_data.items():
                if hasattr(fase, campo):
                    setattr(fase, campo, valor)
            
            self.db.commit()
            self.db.refresh(fase)
            
            return {
                'success': True,
                'fase': {
                    'id': fase.id,
                    'nome': fase.nome,
                    'status': fase.status,
                    'meta_cidades': fase.meta_cidades,
                    'orcamento_previsto': fase.orcamento_previsto
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar fase de planejamento: {e}")
            return {'success': False, 'error': str(e)}
    
    def deletar_fase_planejamento(self, fase_id: int) -> Dict:
        """Deleta uma fase de planejamento"""
        try:
            fase = self.db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
            
            if not fase:
                return {'success': False, 'error': 'Fase não encontrada'}
            
            self.db.delete(fase)
            self.db.commit()
            
            return {'success': True, 'message': 'Fase deletada com sucesso'}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar fase de planejamento: {e}")
            return {'success': False, 'error': str(e)}
    
    # ========== RELATÓRIOS E ANALYTICS ==========
    
    def relatorio_metas_por_tipo(self) -> Dict:
        """Gera relatório de metas agrupadas por tipo"""
        try:
            resultado = {}
            
            # Contar metas por tipo
            tipos = self.db.query(MetasProgressivas.tipo_meta, 
                                self.db.func.count(MetasProgressivas.id).label('total'))\
                         .group_by(MetasProgressivas.tipo_meta)\
                         .all()
            
            for tipo, total in tipos:
                resultado[tipo] = total
            
            return {'success': True, 'tipos': resultado}
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório por tipo: {e}")
            return {'success': False, 'error': str(e)}
    
    def calcular_penetracao_total(self, cidade_id: int) -> Dict:
        """Calcula a penetração total planejada para uma cidade"""
        try:
            # Buscar última meta da cidade (maior mês)
            ultima_meta = self.db.query(MetasProgressivas)\
                .filter(MetasProgressivas.cidade_id == cidade_id)\
                .order_by(desc(MetasProgressivas.mes))\
                .first()
            
            if not ultima_meta:
                return {'success': False, 'error': 'Nenhuma meta encontrada para a cidade'}
            
            # Buscar dados demográficos
            cidade = self.db.query(CidadesDemografia)\
                .filter(CidadesDemografia.id == cidade_id)\
                .first()
            
            penetracao_final = ultima_meta.percentual_penetracao
            publico_atingido = 0
            
            if cidade:
                publico_total = cidade.publico_alvo_15_44_anos or 0
                publico_atingido = int(publico_total * (penetracao_final / 100))
            
            return {
                'success': True,
                'penetracao_final': penetracao_final,
                'publico_atingido': publico_atingido,
                'meta_final_corridas': ultima_meta.meta_corridas,
                'meta_final_motoristas': ultima_meta.meta_motoristas,
                'cidade_nome': ultima_meta.cidade_nome
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular penetração total: {e}")
            return {'success': False, 'error': str(e)}
