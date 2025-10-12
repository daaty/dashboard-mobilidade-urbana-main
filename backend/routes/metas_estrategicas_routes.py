# 🎯 ROUTER PARA METAS ESTRATÉGICAS
# Endpoints dedicados para gerenciar metas progressivas e fases

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import date
import sys
import os

# Adicionar o diretório backend ao Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import get_db
from services.metas_estrategicas_service import MetasEstrategicasService
from services.calculo_progresso_fases import CalculadorProgressoFases, obter_configuracao_calculo_progresso

router = APIRouter(prefix="/api/metas-estrategicas", tags=["Metas Estratégicas"])

# ========== MODELS PYDANTIC ==========

class MetaProgressivaCreate(BaseModel):
    cidade_id: int
    cidade_nome: Optional[str] = None
    mes: int
    percentual_penetracao: float
    meta_corridas: int
    meta_motoristas: int
    meta_receita: Optional[float] = 0
    tipo_meta: Optional[str] = "media"

class MetaProgressivaUpdate(BaseModel):
    cidade_nome: Optional[str] = None
    mes: Optional[int] = None
    percentual_penetracao: Optional[float] = None
    meta_corridas: Optional[int] = None
    meta_motoristas: Optional[int] = None
    meta_receita: Optional[float] = None
    tipo_meta: Optional[str] = None

class FasePlanejamentoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    status: Optional[str] = "planejada"
    meta_cidades: Optional[int] = 0
    orcamento_previsto: Optional[float] = 0
    progresso_percentual: Optional[float] = 0
    ordem: Optional[int] = 1

class FasePlanejamentoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    status: Optional[str] = None
    meta_cidades: Optional[int] = None
    orcamento_previsto: Optional[float] = None
    progresso_percentual: Optional[float] = None
    ordem: Optional[int] = None

# ========== ENDPOINTS METAS PROGRESSIVAS ==========

@router.get("/metas-progressivas")
async def listar_metas_progressivas(
    cidade_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista metas progressivas organizadas por cidade"""
    try:
        service = MetasEstrategicasService(db)
        metas = service.listar_metas_por_cidade()
        return metas  # Retorna lista direta, não objeto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar metas: {str(e)}")

@router.post("/metas-progressivas")
async def criar_meta_progressiva(
    meta: MetaProgressivaCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova meta progressiva"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.criar_meta_progressiva(meta.dict())
        
        if resultado is None:
            raise HTTPException(status_code=400, detail="Erro ao criar meta progressiva")
        
        return {"success": True, "meta": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar meta: {str(e)}")

@router.put("/metas-progressivas/{meta_id}")
async def atualizar_meta_progressiva(
    meta_id: int,
    meta: MetaProgressivaUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza uma meta progressiva existente"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.atualizar_meta_progressiva(meta_id, meta.dict(exclude_unset=True))
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar meta: {str(e)}")

@router.delete("/metas-progressivas/{meta_id}")
async def deletar_meta_progressiva(
    meta_id: int,
    db: Session = Depends(get_db)
):
    """Deleta uma meta progressiva"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.deletar_meta_progressiva(meta_id)
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar meta: {str(e)}")

@router.post("/metas-progressivas/limpar-duplicadas")
async def limpar_metas_duplicadas(db: Session = Depends(get_db)):
    """Remove metas duplicadas do sistema"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.limpar_metas_duplicadas()
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar duplicatas: {str(e)}")

@router.get("/consolidado/{cidade_id}")
async def obter_metas_consolidadas(
    cidade_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna metas consolidadas com dados reais de uma cidade
    
    Retorna todos os períodos (2, 3, 6, 12 meses) com:
    - Metas planejadas (meta_corridas, meta_motoristas, meta_receita)
    - Resultados reais (resultado_corridas, resultado_receita, resultado_motoristas, etc.)
    - Progresso percentual de cada métrica
    
    Dados populados por populate_metas_from_real_data.py
    
    Exemplo: GET /api/metas-estrategicas/consolidado/3 (Matupá)
    """
    try:
        service = MetasEstrategicasService(db)
        resultado = service.obter_metas_consolidadas_por_cidade(cidade_id)
        
        if not resultado['success']:
            raise HTTPException(status_code=404, detail=resultado.get('error', 'Metas não encontradas'))
        
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter metas consolidadas: {str(e)}")

# ========== ENDPOINTS FASES DE PLANEJAMENTO ==========

@router.get("/fases-planejamento")
async def listar_fases_planejamento(db: Session = Depends(get_db)):
    """Lista todas as fases de planejamento com progresso automático calculado"""
    try:
        from services.calculo_progresso_fases import CalculadorProgressoFases
        
        service = MetasEstrategicasService(db)
        fases = service.listar_fases_planejamento()
        
        # Calcular progresso automático para fases não-manuais
        calculadora = CalculadorProgressoFases(db)
        
        for fase in fases:
            # Se não for progresso manual, recalcular automaticamente
            if not fase.get('progresso_manual', False):
                metodo = fase.get('metodo_calculo', 'hibrido')
                try:
                    resultado = calculadora.atualizar_progresso_automatico(fase['id'], metodo)
                    if resultado.get('success'):
                        fase['progresso_percentual'] = resultado['progresso_novo']
                        fase['progresso_automatico'] = True
                        fase['metodo_usado'] = resultado['metodo_usado']
                except Exception as e:
                    print(f"Erro ao calcular progresso automático para fase {fase.get('id', 'N/A')}: {e}")
            else:
                fase['progresso_automatico'] = False
        
        return {"success": True, "fases": fases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar fases: {str(e)}")

@router.post("/fases-planejamento")
async def criar_fase_planejamento(
    fase: FasePlanejamentoCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova fase de planejamento"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.criar_fase_planejamento(fase.dict())
        
        if resultado is None:
            raise HTTPException(status_code=400, detail="Erro ao criar fase de planejamento")
        
        return {"success": True, "fase": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar fase: {str(e)}")

@router.put("/fases-planejamento/{fase_id}")
async def atualizar_fase_planejamento(
    fase_id: int,
    fase: FasePlanejamentoUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza uma fase de planejamento existente"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.atualizar_fase_planejamento(fase_id, fase.dict(exclude_unset=True))
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['message'])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar fase: {str(e)}")

@router.delete("/fases-planejamento/{fase_id}")
async def deletar_fase_planejamento(
    fase_id: int,
    db: Session = Depends(get_db)
):
    """Deleta uma fase de planejamento"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.deletar_fase_planejamento(fase_id)
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['message'])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar fase: {str(e)}")

# ========== ENDPOINTS DE RELATÓRIOS ==========

@router.get("/relatorios/metas-por-tipo")
async def relatorio_metas_por_tipo(db: Session = Depends(get_db)):
    """Gera relatório de metas agrupadas por tipo"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.relatorio_metas_por_tipo()
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get("/relatorios/penetracao-total/{cidade_id}")
async def calcular_penetracao_total(
    cidade_id: int,
    db: Session = Depends(get_db)
):
    """Calcula a penetração total planejada para uma cidade"""
    try:
        service = MetasEstrategicasService(db)
        resultado = service.calcular_penetracao_total(cidade_id)
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular penetração: {str(e)}")

# ========== ENDPOINT DE GERENCIAMENTO ==========

@router.get("/dashboard")
async def dashboard_metas_estrategicas(db: Session = Depends(get_db)):
    """Dashboard consolidado de metas estratégicas"""
    try:
        service = MetasEstrategicasService(db)
        
        # Buscar dados consolidados
        metas_por_cidade = service.listar_metas_por_cidade()
        fases = service.listar_fases_planejamento()
        relatorio_tipos = service.relatorio_metas_por_tipo()
        dashboard_resumo = service.obter_dashboard_resumo()
        
        return {
            "success": True,
            "dashboard": dashboard_resumo.get('resumo', {}),
            "metas_detalhadas": metas_por_cidade,
            "fases": fases,
            "relatorio_tipos": relatorio_tipos.get('tipos', {}) if relatorio_tipos.get('success') else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard: {str(e)}")

# ========== ENDPOINTS DE CÁLCULO AUTOMÁTICO DE PROGRESSO ==========

@router.get("/configuracao-progresso")
async def obter_configuracao_progresso():
    """Retorna as opções de configuração para cálculo de progresso"""
    return obter_configuracao_calculo_progresso()

@router.post("/fases-estrategicas/{fase_id}/calcular-progresso")
async def calcular_progresso_fase(
    fase_id: int,
    metodo: str = "hibrido",
    db: Session = Depends(get_db)
):
    """
    Calcula automaticamente o progresso de uma fase específica
    
    Métodos disponíveis:
    - temporal: Baseado no tempo decorrido
    - orcamentario: Baseado na execução orçamentária  
    - metas: Baseado no cumprimento das metas
    - campanhas: Baseado na performance das campanhas
    - hibrido: Combina todos os métodos (recomendado)
    """
    try:
        calculadora = CalculadorProgressoFases(db)
        resultado = calculadora.atualizar_progresso_automatico(fase_id, metodo)
        
        if not resultado["success"]:
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular progresso: {str(e)}")

@router.post("/fases-estrategicas/recalcular-todas")
async def recalcular_progresso_todas_fases(
    metodo: str = "hibrido",
    db: Session = Depends(get_db)
):
    """Recalcula o progresso de todas as fases ativas"""
    try:
        calculadora = CalculadorProgressoFases(db)
        resultados = calculadora.recalcular_todas_fases(metodo)
        
        sucessos = [r for r in resultados if r.get("success")]
        erros = [r for r in resultados if not r.get("success")]
        
        return {
            "success": True,
            "total_fases": len(resultados),
            "sucessos": len(sucessos),
            "erros": len(erros),
            "detalhes": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recalcular progressos: {str(e)}")

class AlternarProgressoRequest(BaseModel):
    progresso_manual: bool
    progresso_percentual: Optional[float] = None

@router.post("/fases-estrategicas/{fase_id}/alternar-progresso")
async def alternar_modo_progresso(
    fase_id: int,
    request: AlternarProgressoRequest,
    db: Session = Depends(get_db)
):
    """
    Alterna entre progresso manual e automático
    
    - progresso_manual: True para manual, False para automático
    - progresso_percentual: Se manual, define o valor (0-100)
    """
    try:
        from app.models.fases_planejamento import FasesPlanejamento
        from services.calculo_progresso_fases import CalculadorProgressoFases
        
        # Buscar a fase
        fase = db.query(FasesPlanejamento).filter(FasesPlanejamento.id == fase_id).first()
        if not fase:
            raise HTTPException(status_code=404, detail="Fase não encontrada")
        
        # Atualizar modo
        fase.progresso_manual = request.progresso_manual
        
        if request.progresso_manual:
            # Modo manual - usar valor fornecido
            if request.progresso_percentual is not None:
                fase.progresso_percentual = max(0.0, min(100.0, request.progresso_percentual))
            fase.metodo_calculo = "manual"
        else:
            # Modo automático - recalcular
            calculadora = CalculadorProgressoFases(db)
            metodo = getattr(fase, 'metodo_calculo', 'hibrido') if fase.metodo_calculo != "manual" else 'hibrido'
            resultado = calculadora.atualizar_progresso_automatico(fase_id, metodo)
            
            if resultado.get('success'):
                fase.progresso_percentual = resultado['progresso_novo']
                fase.metodo_calculo = resultado['metodo_usado']
        
        db.commit()
        
        return {
            "success": True,
            "fase_id": fase_id,
            "progresso_manual": fase.progresso_manual,
            "progresso_percentual": fase.progresso_percentual,
            "metodo_calculo": fase.metodo_calculo
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao alternar modo de progresso: {str(e)}")
