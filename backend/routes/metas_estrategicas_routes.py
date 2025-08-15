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
from services.metas_estrategicas_service_fixed import MetasEstrategicasService

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
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        return resultado
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

# ========== ENDPOINTS FASES DE PLANEJAMENTO ==========

@router.get("/fases-planejamento")
async def listar_fases_planejamento(db: Session = Depends(get_db)):
    """Lista todas as fases de planejamento"""
    try:
        service = MetasEstrategicasService(db)
        fases = service.listar_fases_planejamento()
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
        
        if not resultado['success']:
            raise HTTPException(status_code=400, detail=resultado['error'])
        
        return resultado
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
            raise HTTPException(status_code=400, detail=resultado['error'])
        
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
            raise HTTPException(status_code=400, detail=resultado['error'])
        
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
        relatorio_tipos = service.gerar_relatorio_por_tipo()
        dashboard_resumo = service.obter_dashboard_resumo()
        
        return {
            "success": True,
            "dashboard": dashboard_resumo.get('resumo', {}),
            "metas_detalhadas": metas_por_cidade,
            "fases": fases,
            "relatorio_tipos": relatorio_tipos.get('relatorio', []) if relatorio_tipos.get('success') else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard: {str(e)}")
