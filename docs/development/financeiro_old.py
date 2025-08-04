from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any
import json
from datetime import datetime, timedelta
from app.database.db import SessionLocal
from app.models.gastos_empresa import GastosEmpresa

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/overview")
async def get_financeiro_overview(
    period: str = "30d",
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retorna overview completo do financeiro da empresa
    """
    try:
        # Calcular data de corte baseada no período
        end_date = datetime.now()
        if period == "hoje":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "7d":
            start_date = end_date - timedelta(days=7)
        else:  # 30d
            start_date = end_date - timedelta(days=30)
        
        # Buscar todos os gastos do período
        result = await db.execute(
            select(GastosEmpresa).filter(
                GastosEmpresa.scraped_at >= start_date,
                GastosEmpresa.scraped_at <= end_date
            )
        )
        gastos_query = result.scalars().all()
        
        # Estruturas para armazenar dados processados
        total_gastos = 0.0
        gastos_por_categoria = {}
        gastos_por_fornecedor = {}
        gastos_por_mes = {}
        gastos_detalhados = []
        documentos_com_nf = 0
        total_documentos = len(gastos_query)
        
        # Processar cada registro
        for gasto in gastos_query:
            try:
                # Parse do JSON dos dados de gastos
                expense_data = json.loads(gasto.expense_data)
                
                # Extrair informações principais
                valor = float(expense_data.get('valor_total', 0))
                descricao = expense_data.get('descricao_item', 'Não informado')
                fornecedor = expense_data.get('fornecedor', 'Não informado')
                data_despesa = expense_data.get('data_despesa', '')
                possui_nf = expense_data.get('possui_nota_fiscal', 0)
                natureza = expense_data.get('natureza_do_gasto', 'Outros')
                tipo_doc = expense_data.get('tipo_documento', 'Não informado')
                
                # Somar valor total
                total_gastos += valor
                
                # Contar documentos com NF
                if possui_nf:
                    documentos_com_nf += 1
                
                # Agrupar por categoria (natureza do gasto)
                if natureza not in gastos_por_categoria:
                    gastos_por_categoria[natureza] = {'total': 0, 'count': 0}
                gastos_por_categoria[natureza]['total'] += valor
                gastos_por_categoria[natureza]['count'] += 1
                
                # Agrupar por fornecedor
                fornecedor_clean = fornecedor[:50] if fornecedor else 'Não informado'
                if fornecedor_clean not in gastos_por_fornecedor:
                    gastos_por_fornecedor[fornecedor_clean] = {'total': 0, 'count': 0}
                gastos_por_fornecedor[fornecedor_clean]['total'] += valor
                gastos_por_fornecedor[fornecedor_clean]['count'] += 1
                
                # Agrupar por mês (se tiver data válida)
                if data_despesa:
                    try:
                        mes_key = data_despesa[:7]  # YYYY-MM
                        if mes_key not in gastos_por_mes:
                            gastos_por_mes[mes_key] = {'total': 0, 'count': 0}
                        gastos_por_mes[mes_key]['total'] += valor
                        gastos_por_mes[mes_key]['count'] += 1
                    except:
                        pass
                
                # Adicionar aos gastos detalhados
                gastos_detalhados.append({
                    'id': gasto.id,
                    'descricao': descricao,
                    'valor': valor,
                    'fornecedor': fornecedor_clean,
                    'data_despesa': data_despesa,
                    'natureza': natureza,
                    'tipo_documento': tipo_doc,
                    'possui_nota_fiscal': bool(possui_nf)
                })
                
            except Exception as e:
                print(f"Erro ao processar gasto {gasto.id}: {e}")
                continue
        
        # Calcular KPIs
        media_gasto_dia = total_gastos / max(1, (end_date - start_date).days) if period != "hoje" else total_gastos
        taxa_documentacao = (documentos_com_nf / max(1, total_documentos)) * 100
        
        # Top fornecedores (os 5 maiores gastos)
        top_fornecedores = sorted(
            [{'nome': k, 'total': v['total'], 'transacoes': v['count']} 
             for k, v in gastos_por_fornecedor.items()],
            key=lambda x: x['total'],
            reverse=True
        )[:5]
        
        # Top categorias
        top_categorias = sorted(
            [{'nome': k, 'total': v['total'], 'transacoes': v['count']} 
             for k, v in gastos_por_categoria.items()],
            key=lambda x: x['total'],
            reverse=True
        )[:5]
        
        # Tendência (comparar com período anterior)
        periodo_anterior_start = start_date - (end_date - start_date)
        result_anterior = await db.execute(
            select(GastosEmpresa).filter(
                GastosEmpresa.scraped_at >= periodo_anterior_start,
                GastosEmpresa.scraped_at < start_date
            )
        )
        gastos_anterior = result_anterior.scalars().all()
        
        total_anterior = 0.0
        for gasto in gastos_anterior:
            try:
                expense_data = json.loads(gasto.expense_data)
                total_anterior += float(expense_data.get('valor_total', 0))
            except:
                continue
        
        # Calcular variação percentual
        if total_anterior > 0:
            variacao_percentual = ((total_gastos - total_anterior) / total_anterior) * 100
        else:
            variacao_percentual = 0
        
        # Preparar dados para gráficos mensais
        gastos_mensais = []
        for mes, dados in sorted(gastos_por_mes.items()):
            gastos_mensais.append({
                'mes': mes,
                'total': dados['total'],
                'transacoes': dados['count']
            })
        
        # Preparar resposta
        response = {
            'total_gastos': round(total_gastos, 2),
            'total_receitas': 0.0,  # Placeholder para futuras receitas
            'saldo_liquido': round(-total_gastos, 2),  # Negativo por ser só gastos
            'media_gasto_diario': round(media_gasto_dia, 2),
            'total_transacoes': total_documentos,
            'taxa_documentacao': round(taxa_documentacao, 2),
            'variacao_percentual': round(variacao_percentual, 2),
            'periodo_dias': (end_date - start_date).days if period != "hoje" else 1,
            
            # Distribuições
            'gastos_por_categoria': gastos_por_categoria,
            'gastos_por_fornecedor': gastos_por_fornecedor,
            'gastos_mensais': gastos_mensais,
            
            # Tops
            'top_fornecedores': top_fornecedores,
            'top_categorias': top_categorias,
            
            # Detalhes
            'gastos_detalhados': gastos_detalhados[:10],  # Primeiros 10
            
            # Métricas avançadas
            'metricas_qualidade': {
                'documentos_com_nf': documentos_com_nf,
                'documentos_sem_nf': total_documentos - documentos_com_nf,
                'taxa_conformidade': round(taxa_documentacao, 2)
            },
            
            # Placeholder para receitas (quando implementadas)
            'receitas_futuras': {
                'total_receitas': 0.0,
                'receitas_mensais': [],
                'margem_liquida': 0.0
            }
        }
        
        return response
        
    except Exception as e:
        print(f"Erro ao buscar dados financeiros: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
