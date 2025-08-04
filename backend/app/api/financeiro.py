from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, extract
from typing import Optional
from datetime import datetime, timedelta, date
from app.database.db import SessionLocal
from app.models.gastos_empresa import GastosEmpresa
from collections import defaultdict
import calendar

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

def parse_date(date_str):
    """Função para converter string de data para objeto date"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except:
            return None

def parse_valor(valor_str):
    """Função para converter string de valor para float"""
    if not valor_str:
        return 0.0
    try:
        # Remove caracteres não numéricos exceto ponto e vírgula
        valor_clean = str(valor_str).replace(',', '.').replace('R$', '').replace(' ', '')
        return float(valor_clean)
    except:
        return 0.0

def agrupar_documentos_relacionados(gastos_lista):
    """
    Agrupa documentos relacionados em uma única entrada
    REGRA: Só agrupa comprovantes que POSSUEM nota fiscal (possui_nota_fiscal = 1)
    - Comprovante SEM NF (possui_nota_fiscal = 0) → Mostra separado
    - Comprovante COM NF (possui_nota_fiscal = 1) → Agrupa com NF usando id_documento_vinculado
    """
    documentos_agrupados = {}
    comprovantes_com_nf = {}
    
    # Primeiro passo: processar todos os documentos
    for gasto in gastos_lista:
        if gasto.tipo_documento == "Nota Fiscal":
            # Sempre criar entrada para Nota Fiscal
            documentos_agrupados[gasto.id] = {
                "id": gasto.id,
                "data_despesa": gasto.data_despesa,
                "valor_total": parse_valor(gasto.valor_total),
                "descricao_item": gasto.descricao_item or "",
                "fornecedor": gasto.fornecedor or "",
                "tipo_documento": gasto.tipo_documento,
                "natureza_do_gasto": gasto.natureza_do_gasto or "",
                "possui_nota_fiscal": True,
                "numero_nota_fiscal": gasto.numero_nota_fiscal or "",
                "documentos": [
                    {
                        "tipo": "Nota Fiscal",
                        "url": gasto.arquivo_drive_url or "",
                        "id": gasto.id
                    }
                ]
            }
        
        elif gasto.tipo_documento == "Comprovante de Pagamento":
            if gasto.possui_nota_fiscal and gasto.id_documento_vinculado:
                # Comprovante COM NF - vai ser vinculado à NF
                comprovantes_com_nf[gasto.id_documento_vinculado] = {
                    "tipo": "Comprovante de Pagamento",
                    "url": gasto.arquivo_drive_url or "",
                    "id": gasto.id
                }
            else:
                # Comprovante SEM NF - criar entrada separada
                documentos_agrupados[gasto.id] = {
                    "id": gasto.id,
                    "data_despesa": gasto.data_despesa,
                    "valor_total": parse_valor(gasto.valor_total),
                    "descricao_item": gasto.descricao_item or "",
                    "fornecedor": gasto.fornecedor or "",
                    "tipo_documento": gasto.tipo_documento,
                    "natureza_do_gasto": gasto.natureza_do_gasto or "",
                    "possui_nota_fiscal": False,
                    "numero_nota_fiscal": "",
                    "documentos": [
                        {
                            "tipo": "Comprovante de Pagamento",
                            "url": gasto.arquivo_drive_url or "",
                            "id": gasto.id
                        }
                    ]
                }
        
        else:
            # Outros tipos de documento
            documentos_agrupados[gasto.id] = {
                "id": gasto.id,
                "data_despesa": gasto.data_despesa,
                "valor_total": parse_valor(gasto.valor_total),
                "descricao_item": gasto.descricao_item or "",
                "fornecedor": gasto.fornecedor or "",
                "tipo_documento": gasto.tipo_documento or "Outros",
                "natureza_do_gasto": gasto.natureza_do_gasto or "",
                "possui_nota_fiscal": bool(gasto.possui_nota_fiscal),
                "numero_nota_fiscal": gasto.numero_nota_fiscal or "",
                "documentos": [
                    {
                        "tipo": gasto.tipo_documento or "Outros",
                        "url": gasto.arquivo_drive_url or "",
                        "id": gasto.id
                    }
                ]
            }
    
    # Segundo passo: vincular comprovantes COM NF às suas NFs
    for id_nf, comprovante in comprovantes_com_nf.items():
        if id_nf in documentos_agrupados:
            documentos_agrupados[id_nf]["documentos"].append(comprovante)
    
    return list(documentos_agrupados.values())

@router.get("/overview")
async def get_financial_overview(
    periodo: Optional[int] = Query(30, description="Número de dias para análise"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para métricas financeiras gerais da empresa
    """
    try:
        # Data limite baseada no período
        data_limite = datetime.now().date() - timedelta(days=periodo)
        
        # Buscar todos os gastos (sem filtro de data inicialmente)
        result = await db.execute(select(GastosEmpresa))
        gastos_data = result.scalars().all()
        
        if not gastos_data:
            return {
                "total_gastos": 0.0,
                "total_despesas": 0,
                "media_gastos_dia": 0.0,
                "gastos_por_categoria": {},
                "gastos_por_fornecedor": {},
                "gastos_por_tipo_documento": {},
                "resumo_mensal": {},
                "top_gastos": [],
                "periodo_dias": periodo,
                "data_inicio": data_limite.isoformat(),
                "data_fim": datetime.now().date().isoformat()
            }
        
        # Filtrar por data após buscar (devido ao formato string)
        gastos_filtrados = []
        for gasto in gastos_data:
            data_gasto = parse_date(gasto.data_despesa)
            if data_gasto and data_gasto >= data_limite:
                gastos_filtrados.append(gasto)
        
        gastos_data = gastos_filtrados
        
        # Aplicar agrupamento para evitar duplicação nas métricas
        gastos_agrupados_para_metricas = agrupar_documentos_relacionados(gastos_data)
        
        # Recalcular métricas usando dados agrupados
        total_gastos = sum(gasto["valor_total"] for gasto in gastos_agrupados_para_metricas)
        total_despesas = len(gastos_agrupados_para_metricas)
        media_gastos_dia = total_gastos / periodo if periodo > 0 else 0
        
        # Agrupar por categoria (usando dados agrupados)
        gastos_por_categoria = defaultdict(float)
        for gasto in gastos_agrupados_para_metricas:
            categoria = gasto["natureza_do_gasto"] or "Outros"
            gastos_por_categoria[categoria] += gasto["valor_total"]
        
        # Agrupar por fornecedor (usando dados agrupados)
        gastos_por_fornecedor = defaultdict(float)
        for gasto in gastos_agrupados_para_metricas:
            fornecedor = gasto["fornecedor"] or "Não informado"
            gastos_por_fornecedor[fornecedor] += gasto["valor_total"]
        
        # Agrupar por tipo de documento (usando dados originais para estatísticas de documentos)
        gastos_por_tipo_documento = defaultdict(float)
        for gasto in gastos_data:
            tipo = gasto.tipo_documento or "Outros"
            gastos_por_tipo_documento[tipo] += parse_valor(gasto.valor_total)
        
        # Resumo mensal (usando dados agrupados)
        resumo_mensal = defaultdict(lambda: {"valor": 0.0, "quantidade": 0})
        for gasto in gastos_agrupados_para_metricas:
            data_gasto = parse_date(gasto["data_despesa"])
            if data_gasto:
                mes_ano = data_gasto.strftime("%Y-%m")
                resumo_mensal[mes_ano]["valor"] += gasto["valor_total"]
                resumo_mensal[mes_ano]["quantidade"] += 1
        
        # Aplicar agrupamento e pegar os top 10
        gastos_agrupados = agrupar_documentos_relacionados(gastos_data)
        top_gastos_formatted = sorted(gastos_agrupados, key=lambda x: x["valor_total"], reverse=True)[:10]
        
        # Métricas de documentação (usando dados agrupados)
        gastos_com_nf = sum(1 for gasto in gastos_agrupados_para_metricas if gasto["possui_nota_fiscal"])
        taxa_documentacao = (gastos_com_nf / total_despesas * 100) if total_despesas > 0 else 0
        
        # Tendência (últimos vs penúltimos dias)
        variacao_percentual = 0  # Simplificado por enquanto
        
        return {
            "total_gastos": round(total_gastos, 2),
            "total_despesas": total_despesas,
            "media_gastos_dia": round(media_gastos_dia, 2),
            "taxa_documentacao": round(taxa_documentacao, 1),
            "variacao_percentual": round(variacao_percentual, 1),
            "gastos_por_categoria": dict(gastos_por_categoria),
            "gastos_por_fornecedor": dict(sorted(gastos_por_fornecedor.items(), key=lambda x: x[1], reverse=True)[:10]),
            "gastos_por_tipo_documento": dict(gastos_por_tipo_documento),
            "resumo_mensal": dict(resumo_mensal),
            "top_gastos": top_gastos_formatted,
            "periodo_dias": periodo,
            "data_inicio": data_limite.isoformat(),
            "data_fim": datetime.now().date().isoformat(),
            "resumo_kpis": {
                "gastos_com_nf": gastos_com_nf,
                "gastos_sem_nf": total_despesas - gastos_com_nf,
                "maior_gasto": max([g["valor_total"] for g in gastos_agrupados_para_metricas]) if gastos_agrupados_para_metricas else 0,
                "menor_gasto": min([g["valor_total"] for g in gastos_agrupados_para_metricas if g["valor_total"] > 0]) if gastos_agrupados_para_metricas else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados financeiros: {str(e)}")

@router.get("/categorias")
async def get_gastos_por_categoria(
    periodo: Optional[int] = Query(30, description="Número de dias para análise"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint detalhado para gastos por categoria
    """
    try:
        data_limite = datetime.now().date() - timedelta(days=periodo)
        
        result = await db.execute(
            select(GastosEmpresa).where(
                GastosEmpresa.data_despesa >= data_limite
            )
        )
        gastos_data = result.scalars().all()
        
        categorias_detalhadas = defaultdict(lambda: {
            "total": 0.0, 
            "quantidade": 0, 
            "media": 0.0, 
            "gastos": []
        })
        
        for gasto in gastos_data:
            categoria = gasto.natureza_do_gasto or "Outros"
            valor = float(gasto.valor_total or 0)
            
            categorias_detalhadas[categoria]["total"] += valor
            categorias_detalhadas[categoria]["quantidade"] += 1
            categorias_detalhadas[categoria]["gastos"].append({
                "id": gasto.id,
                "data": gasto.data_despesa.isoformat() if gasto.data_despesa else None,
                "valor": valor,
                "descricao": gasto.descricao_item or "",
                "fornecedor": gasto.fornecedor or ""
            })
        
        # Calcular médias
        for categoria in categorias_detalhadas:
            dados = categorias_detalhadas[categoria]
            dados["media"] = dados["total"] / dados["quantidade"] if dados["quantidade"] > 0 else 0
            dados["gastos"] = sorted(dados["gastos"], key=lambda x: x["valor"], reverse=True)[:5]
        
        return dict(categorias_detalhadas)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar categorias: {str(e)}")

@router.get("/fornecedores")
async def get_top_fornecedores(
    periodo: Optional[int] = Query(30, description="Número de dias para análise"),
    limit: Optional[int] = Query(20, description="Número máximo de fornecedores"),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para ranking de fornecedores
    """
    try:
        data_limite = datetime.now().date() - timedelta(days=periodo)
        
        result = await db.execute(
            select(GastosEmpresa).where(
                GastosEmpresa.data_despesa >= data_limite
            )
        )
        gastos_data = result.scalars().all()
        
        fornecedores_stats = defaultdict(lambda: {
            "total_gasto": 0.0,
            "quantidade_compras": 0,
            "ticket_medio": 0.0,
            "ultima_compra": None,
            "tipos_documento": set()
        })
        
        for gasto in gastos_data:
            fornecedor = gasto.fornecedor or "Não informado"
            valor = float(gasto.valor_total or 0)
            
            fornecedores_stats[fornecedor]["total_gasto"] += valor
            fornecedores_stats[fornecedor]["quantidade_compras"] += 1
            fornecedores_stats[fornecedor]["tipos_documento"].add(gasto.tipo_documento or "Outros")
            
            if gasto.data_despesa:
                if (not fornecedores_stats[fornecedor]["ultima_compra"] or 
                    gasto.data_despesa > fornecedores_stats[fornecedor]["ultima_compra"]):
                    fornecedores_stats[fornecedor]["ultima_compra"] = gasto.data_despesa
        
        # Processar dados finais
        fornecedores_processados = []
        for fornecedor, stats in fornecedores_stats.items():
            stats["ticket_medio"] = stats["total_gasto"] / stats["quantidade_compras"]
            stats["tipos_documento"] = list(stats["tipos_documento"])
            stats["ultima_compra"] = stats["ultima_compra"].isoformat() if stats["ultima_compra"] else None
            
            fornecedores_processados.append({
                "fornecedor": fornecedor,
                **stats
            })
        
        # Ordenar por total gasto e limitar
        fornecedores_processados.sort(key=lambda x: x["total_gasto"], reverse=True)
        
        return {
            "fornecedores": fornecedores_processados[:limit],
            "total_fornecedores": len(fornecedores_processados),
            "periodo_dias": periodo
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fornecedores: {str(e)}")
