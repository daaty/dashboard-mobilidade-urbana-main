#!/usr/bin/env python3
"""
Script para popular automaticamente as tabelas FasesPlanejamento e MetasProgressivas
com dados baseados no planejamento estratégico do projeto.
"""

import sys
import os
import requests
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def popular_fases_planejamento():
    """Popula tabela fases_planejamento com as 3 fases do projeto"""
    
    print("🏗️ POPULANDO FASES DE PLANEJAMENTO...")
    print("=" * 50)
    
    # Dados das fases baseados no planejamento estratégico
    fases_data = [
        {
            "nome": "Fase 1",
            "descricao": "Lançamento inicial - Cidades estratégicas com maior potencial",
            "data_inicio": "2025-08-01",
            "data_fim": "2025-09-30",
            "status": "em_execucao",
            "progresso_percentual": 75.0,
            "orcamento_previsto": 50000.0,
            "orcamento_empenhado": 37500.0,
            "orcamento_pago": 25000.0,
            "meta_cidades": 4,
            "meta_motoristas": 80,
            "meta_corridas": 200,
            "meta_receita": 15000.0,
            "resultado_cidades": 4,
            "resultado_motoristas": 75,
            "resultado_corridas": 185,
            "resultado_receita": 12500.0,
            "prazo_meses": 2,
            "responsavel": "Equipe de Expansão",
            "observacoes": "Fase com foco em cidades com dados já validados"
        },
        {
            "nome": "Fase 2", 
            "descricao": "Expansão regional - Cidades de médio porte",
            "data_inicio": "2025-09-01",
            "data_fim": "2025-10-31",
            "status": "planejada",
            "progresso_percentual": 10.0,
            "orcamento_previsto": 75000.0,
            "orcamento_empenhado": 15000.0,
            "orcamento_pago": 0.0,
            "meta_cidades": 3,
            "meta_motoristas": 120,
            "meta_corridas": 350,
            "meta_receita": 28000.0,
            "resultado_cidades": 1,
            "resultado_motoristas": 15,
            "resultado_corridas": 25,
            "resultado_receita": 2000.0,
            "prazo_meses": 2,
            "responsavel": "Equipe de Expansão",
            "observacoes": "Fase focada em consolidação regional"
        },
        {
            "nome": "Fase 3",
            "descricao": "Consolidação - Cidades complementares e otimização",
            "data_inicio": "2025-11-01", 
            "data_fim": "2025-12-31",
            "status": "planejada",
            "progresso_percentual": 0.0,
            "orcamento_previsto": 60000.0,
            "orcamento_empenhado": 0.0,
            "orcamento_pago": 0.0,
            "meta_cidades": 3,
            "meta_motoristas": 100,
            "meta_corridas": 300,
            "meta_receita": 25000.0,
            "resultado_cidades": 0,
            "resultado_motoristas": 0,
            "resultado_corridas": 0,
            "resultado_receita": 0.0,
            "prazo_meses": 2,
            "responsavel": "Equipe de Expansão",
            "observacoes": "Fase de consolidação e otimização operacional"
        }
    ]
    
    # Tentar criar via API se disponível, senão usar endpoint personalizado
    api_url = "http://localhost:8000/api/fases-planejamento"
    
    fases_criadas = []
    for fase_data in fases_data:
        try:
            print(f"📅 Criando {fase_data['nome']}...")
            # POST para API
            response = requests.post("http://localhost:8000/api/fases-planejamento", json=fase_data)
            if response.status_code == 200 or response.status_code == 201:
                print(f"✅ {fase_data['nome']} criada na API!")
                fases_criadas.append(response.json())
            else:
                print(f"❌ Erro ao criar {fase_data['nome']} na API: {response.text}")
        except Exception as e:
            print(f"❌ Erro ao criar {fase_data['nome']}: {e}")
    print(f"\n✅ {len(fases_criadas)}/3 fases configuradas!")
    return fases_criadas

def popular_metas_progressivas():
    """Popula metas progressivas para cada cidade com dados automáticos"""
    
    print("\n🎯 POPULANDO METAS PROGRESSIVAS...")
    print("=" * 50)
    
    # Primeiro, buscar cidades disponíveis
    try:
        response = requests.get("http://localhost:8000/api/cidades")
        if response.status_code == 200:
            cidades = response.json()
            print(f"🏙️ Encontradas {len(cidades)} cidades para criar metas")
        else:
            print("❌ Não foi possível buscar cidades")
            return []
    except:
        print("❌ API não disponível para buscar cidades")
        return []
    
    metas_criadas = []
    estrategias_percentuais = [
        {"mes": 1, "percentual": 0.5, "tipo": "muito_baixa"},
        {"mes": 2, "percentual": 1.0, "tipo": "baixa"},
        {"mes": 3, "percentual": 2.0, "tipo": "media"},
        {"mes": 6, "percentual": 5.0, "tipo": "alta"},
        {"mes": 12, "percentual": 10.0, "tipo": "agressiva"}
    ]
    for cidade in cidades:
        nome_cidade = cidade['cidade']
        cidade_id = cidade['id']
        publico_alvo = cidade.get('publico_alvo_15_44_anos', cidade.get('populacao_estimada_2024', 10000) * 0.4)
        print(f"\n📊 Criando metas para {nome_cidade} (ID: {cidade_id})")
        print(f"   👥 Público-alvo: {publico_alvo:,.0f} pessoas")
        for estrategia in estrategias_percentuais:
            mes = estrategia["mes"]
            percentual = estrategia["percentual"]
            tipo = estrategia["tipo"]
            usuarios_meta = int(publico_alvo * (percentual / 100))
            corridas_por_usuario_mes = 2.5
            motoristas_por_100_corridas = 2.5
            receita_por_corrida = 2.50
            meta_corridas = int(usuarios_meta * corridas_por_usuario_mes)
            meta_motoristas = max(1, int(meta_corridas * (motoristas_por_100_corridas / 100)))
            meta_receita = meta_corridas * receita_por_corrida
            investimento_previsto = (meta_motoristas * 50) + (meta_corridas * 0.50)
            meta_data = {
                "cidade_id": cidade_id,
                "mes": mes,
                "percentual_publico": percentual,
                "tipo_meta": tipo,
                "meta_corridas": meta_corridas,
                "meta_motoristas": meta_motoristas,
                "meta_usuarios_ativos": usuarios_meta,
                "meta_receita": meta_receita,
                "investimento_previsto": investimento_previsto,
                "estrategia": f"Atingir {percentual}% do público-alvo em {mes} mês(es)",
                "status": "ativa"
            }
            print(f"   🎯 Mês {mes:2d} ({tipo:12s}): {meta_corridas:3d} corridas, {meta_motoristas:2d} motoristas, R$ {meta_receita:6.0f}")
            try:
                # Enviar apenas campos aceitos pelo modelo
                meta_payload = {k: v for k, v in meta_data.items() if k in [
                    "cidade_id", "fase_id", "mes", "percentual_publico", "tipo_meta", "meta_corridas", "meta_motoristas", "meta_usuarios_ativos", "meta_receita", "investimento_previsto", "estrategia", "status", "observacoes"
                ]}
                response = requests.post("http://localhost:8000/api/metas-progressivas", json=meta_payload)
                if response.status_code == 200 or response.status_code == 201:
                    metas_criadas.append(response.json())
                else:
                    print(f"      ❌ Erro ao criar meta na API: {response.text}")
            except Exception as e:
                print(f"      ❌ Erro ao criar meta: {e}")
    print(f"\n✅ {len(metas_criadas)} metas progressivas configuradas!")
    print(f"📈 Cobertura: {len(cidades)} cidades × {len(estrategias_percentuais)} períodos")
    return metas_criadas

def gerar_relatorio_consolidado(fases_criadas, metas_criadas):
    """Gera relatório consolidado das configurações"""
    
    print("\n📋 RELATÓRIO CONSOLIDADO")
    print("=" * 50)
    
    # Resumo das fases
    total_orcamento = sum([f['orcamento_previsto'] for f in fases_criadas])
    total_meta_cidades = sum([f['meta_cidades'] for f in fases_criadas])
    total_meta_corridas = sum([f['meta_corridas'] for f in fases_criadas])
    
    print(f"💰 Orçamento total planejado: R$ {total_orcamento:,.2f}")
    print(f"🏙️ Total de cidades no plano: {total_meta_cidades}")
    print(f"🚗 Total de corridas planejadas: {total_meta_corridas:,}")
    
    # Resumo das metas
    cidades_com_metas = len(set([m['cidade_id'] for m in metas_criadas]))
    total_investimento_metas = sum([m['investimento_previsto'] for m in metas_criadas])
    
    print(f"📊 Cidades com metas configuradas: {cidades_com_metas}")
    print(f"💵 Investimento total estimado (metas): R$ {total_investimento_metas:,.2f}")
    
    # Próximos passos
    print(f"\n🔄 PRÓXIMOS PASSOS:")
    print(f"✅ 1. Criar APIs para FasesPlanejamento")
    print(f"✅ 2. Criar APIs para MetasProgressivas") 
    print(f"✅ 3. Integrar no frontend MetasCidades")
    print(f"✅ 4. Criar dashboards de acompanhamento")
    
    return {
        "fases": len(fases_criadas),
        "metas": len(metas_criadas),
        "orcamento_total": total_orcamento,
        "investimento_total": total_investimento_metas
    }

if __name__ == "__main__":
    print("🚀 SCRIPT DE POPULAÇÃO AUTOMÁTICA")
    print("=" * 50)
    print("Criando dados estratégicos para FasesPlanejamento e MetasProgressivas")
    
    # Executar população
    fases_criadas = popular_fases_planejamento()
    metas_criadas = popular_metas_progressivas()
    
    # Gerar relatório
    relatorio = gerar_relatorio_consolidado(fases_criadas, metas_criadas)
    
    print(f"\n🎉 PROCESSO CONCLUÍDO!")
    print(f"📈 Sistema agora tem base de dados estratégicos para dashboards avançados!")
