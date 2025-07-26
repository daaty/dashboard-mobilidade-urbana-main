from fastapi import APIRouter
from backend.app.models.dashboard import FinanceiroResponse, OperacionalResponse, ExecutivoResponse, PreditivoResponse

router = APIRouter()

@router.get("/dashboard/financeiro", response_model=FinanceiroResponse, tags=["Dashboards"])
def get_financeiro():
    return FinanceiroResponse(receita_total=100000.0, despesas=40000.0, lucro=60000.0)

@router.get("/dashboard/operacional", response_model=OperacionalResponse, tags=["Dashboards"])
def get_operacional():
    return OperacionalResponse(viagens=1200, frota_ativa=45, km_rodados=35000.0)

@router.get("/dashboard/executivo", response_model=ExecutivoResponse, tags=["Dashboards"])
def get_executivo():
    return ExecutivoResponse(resumo="Resumo executivo simulado", indicadores={"NPS": 85, "Satisfação": 92})

@router.get("/dashboard/preditivo", response_model=PreditivoResponse, tags=["Dashboards"])
def get_preditivo():
    return PreditivoResponse(previsao_receita=120000.0, previsao_viagens=1300)
