"""
🧠 FERRAMENTAS DE ANÁLISE E REASONING PARA MOBILIDADE URBANA
Tools especializadas em análise de negócio, KPIs e geração de insights
"""

import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from agno.tools import Toolkit
from agno.utils.log import logger


class BusinessAnalysisTools(Toolkit):
    """Ferramentas de análise de negócio e geração de insights"""
    
    def __init__(self, **kwargs):
        self.kpis_industry = {
            "taxa_cancelamento_ideal": 15.0,  # %
            "taxa_conversao_motoristas": 3.0,  # %
            "rating_minimo_aceitavel": 4.0,
            "corridas_por_motorista_dia": 8,
            "roi_campanha_minimo": 150.0,  # %
            "penetracao_mercado_meta": 2.5,  # %
        }
        
        # 🎯 CORREÇÃO CRÍTICA: Adicionar métodos explicitamente à lista de tools
        tools = [
            self.calculate_business_kpis,
            self.generate_growth_strategy,
            self.analyze_market_trends,
            self.competitive_analysis,
            self.financial_health_check
        ]
        
        super().__init__(name="business_analysis_tools", tools=tools, **kwargs)
        print(f"✅ [INIT] BusinessAnalysisTools inicializado com {len(tools)} ferramentas")
    
    def calculate_business_kpis(self, data: str) -> str:
        """
        Calcula KPIs de negócio a partir dos dados fornecidos.
        
        Args:
            data: JSON string com dados do dashboard
            
        Returns:
            Análise detalhada dos KPIs calculados
        """
        try:
            parsed_data = json.loads(data)
            
            kpis = {}
            recommendations = []
            alerts = []
            
            # Taxa de Cancelamento
            if "metricas_principais" in parsed_data:
                metrics = parsed_data["metricas_principais"]
                total_rides = metrics.get("corridas_concluidas", 0) + metrics.get("corridas_canceladas", 0)
                
                if total_rides > 0:
                    cancellation_rate = (metrics.get("corridas_canceladas", 0) / total_rides) * 100
                    kpis["taxa_cancelamento"] = round(cancellation_rate, 2)
                    
                    if cancellation_rate > self.kpis_industry["taxa_cancelamento_ideal"]:
                        alerts.append(f"⚠️ Taxa de cancelamento alta: {cancellation_rate:.1f}% (ideal: <{self.kpis_industry['taxa_cancelamento_ideal']}%)")
                        recommendations.append("Investigar motivos de cancelamento e melhorar matching motorista-passageiro")
            
            # ROI das Campanhas
            if "total_gastos" in parsed_data and "corridas_concluidas" in parsed_data.get("metricas_principais", {}):
                gastos = parsed_data.get("total_gastos", 0)
                corridas = parsed_data["metricas_principais"]["corridas_concluidas"]
                
                if gastos > 0:
                    # Assumindo receita média de R$ 12 por corrida
                    receita_estimada = corridas * 12
                    roi = ((receita_estimada - gastos) / gastos) * 100
                    kpis["roi_estimado"] = round(roi, 2)
                    
                    if roi < self.kpis_industry["roi_campanha_minimo"]:
                        alerts.append(f"📉 ROI baixo: {roi:.1f}% (meta: >{self.kpis_industry['roi_campanha_minimo']}%)")
                        recommendations.append("Otimizar gastos de marketing e focar em campanhas mais efetivas")
            
            # Produtividade dos Motoristas
            if "total_drivers" in parsed_data and "corridas_concluidas" in parsed_data.get("metricas_principais", {}):
                drivers = parsed_data["total_drivers"]
                corridas = parsed_data["metricas_principais"]["corridas_concluidas"]
                
                if drivers > 0:
                    # Assumindo período de 30 dias
                    corridas_por_motorista_mes = corridas / drivers
                    corridas_por_motorista_dia = corridas_por_motorista_mes / 30
                    kpis["corridas_por_motorista_dia"] = round(corridas_por_motorista_dia, 2)
                    
                    if corridas_por_motorista_dia < self.kpis_industry["corridas_por_motorista_dia"]:
                        alerts.append(f"⚡ Baixa produtividade: {corridas_por_motorista_dia:.1f} corridas/dia (meta: {self.kpis_industry['corridas_por_motorista_dia']})")
                        recommendations.append("Implementar incentivos para aumentar atividade dos motoristas")
            
            analysis = {
                "kpis_calculados": kpis,
                "alertas_criticos": alerts,
                "recomendacoes_estrategicas": recommendations,
                "benchmarks_industria": self.kpis_industry,
                "data_analise": datetime.now().isoformat()
            }
            
            return json.dumps(analysis, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return f"Erro ao calcular KPIs: {str(e)}"
    
    def generate_growth_strategy(self, cities_data: str, goals_data: str) -> str:
        """
        Gera estratégia de crescimento baseada em dados de cidades e metas.
        
        Args:
            cities_data: JSON com dados demográficos das cidades
            goals_data: JSON com metas estratégicas
            
        Returns:
            Estratégia de crescimento detalhada
        """
        try:
            cities = json.loads(cities_data)
            goals = json.loads(goals_data)
            
            strategy = {
                "fase_atual": "Análise e Planejamento",
                "cidades_prioritarias": [],
                "estrategias_por_cidade": {},
                "cronograma_expansao": {},
                "investimento_recomendado": {}
            }
            
            # Analisar potencial de cada cidade
            if isinstance(cities, list):
                for city in cities:
                    city_name = city.get("nome", "")
                    population = city.get("populacao", 0)
                    target_audience = city.get("publico_alvo", 0)
                    
                    if population > 0 and target_audience > 0:
                        penetration_potential = (target_audience / population) * 100
                        
                        # Classificar prioridade baseada no potencial
                        if penetration_potential > 30 and population > 50000:
                            priority = "Alta"
                            investment = population * 0.5  # R$ 0.50 per capita
                        elif penetration_potential > 20:
                            priority = "Média"
                            investment = population * 0.3
                        else:
                            priority = "Baixa"
                            investment = population * 0.1
                        
                        strategy["estrategias_por_cidade"][city_name] = {
                            "prioridade": priority,
                            "potencial_penetracao": round(penetration_potential, 2),
                            "investimento_sugerido": round(investment, 2),
                            "meta_motoristas_ano1": max(10, int(target_audience * 0.001)),
                            "meta_corridas_mes": max(100, int(target_audience * 0.01))
                        }
                        
                        if priority == "Alta":
                            strategy["cidades_prioritarias"].append(city_name)
            
            # Cronograma de expansão
            priority_cities = strategy["cidades_prioritarias"][:3]  # Top 3
            for i, city in enumerate(priority_cities):
                quarter = f"Q{i+1}/2025"
                strategy["cronograma_expansao"][quarter] = {
                    "cidade_foco": city,
                    "atividades": [
                        "Lançamento de campanha de recrutamento",
                        "Parceria com estabelecimentos locais",
                        "Programa de incentivos para primeiros usuários"
                    ]
                }
            
            return json.dumps(strategy, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return f"Erro ao gerar estratégia: {str(e)}"
    
    def analyze_market_trends(self, historical_data: str) -> str:
        """
        Analisa tendências de mercado baseado em dados históricos.
        
        Args:
            historical_data: JSON com evolução histórica das métricas
            
        Returns:
            Análise de tendências e projeções
        """
        try:
            data = json.loads(historical_data)
            trends = {
                "tendencias_identificadas": [],
                "projecoes_30_dias": {},
                "sazonalidade": {},
                "recomendacoes_taticas": []
            }
            
            if "evolucao" in data and len(data["evolucao"]) > 0:
                evolution = data["evolucao"]
                
                # Calcular crescimento
                recent_values = [item.get("value", 0) for item in evolution[-7:]]  # Últimos 7 dias
                older_values = [item.get("value", 0) for item in evolution[:7]]   # Primeiros 7 dias
                
                if recent_values and older_values:
                    recent_avg = statistics.mean(recent_values)
                    older_avg = statistics.mean(older_values)
                    
                    if older_avg > 0:
                        growth_rate = ((recent_avg - older_avg) / older_avg) * 100
                        
                        if growth_rate > 10:
                            trends["tendencias_identificadas"].append("📈 Crescimento acelerado detectado")
                            trends["recomendacoes_taticas"].append("Aumentar capacidade operacional")
                        elif growth_rate < -10:
                            trends["tendencias_identificadas"].append("📉 Declínio preocupante")
                            trends["recomendacoes_taticas"].append("Investigar causas e implementar ações corretivas")
                        else:
                            trends["tendencias_identificadas"].append("📊 Crescimento estável")
                
                # Projeção baseada na tendência
                if recent_values:
                    current_avg = statistics.mean(recent_values)
                    trends["projecoes_30_dias"] = {
                        "cenario_conservador": round(current_avg * 0.9, 2),
                        "cenario_provavel": round(current_avg, 2),
                        "cenario_otimista": round(current_avg * 1.2, 2)
                    }
            
            return json.dumps(trends, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return f"Erro ao analisar tendências: {str(e)}"
    
    def competitive_analysis(self, market_data: str) -> str:
        """
        Realiza análise competitiva do mercado de mobilidade urbana.
        
        Args:
            market_data: JSON com dados de mercado e penetração
            
        Returns:
            Análise competitiva e posicionamento
        """
        competitive_landscape = {
            "posicionamento_atual": "Challenger em mercados pequenos/médios",
            "vantagens_competitivas": [
                "Foco em cidades menores (menos concorrência)",
                "Operação mais enxuta",
                "Relacionamento próximo com motoristas"
            ],
            "ameacas_competitivas": [
                "Entrada de players maiores",
                "Guerra de preços",
                "Pressão regulatória"
            ],
            "oportunidades": [
                "Mercados inexplorados no interior",
                "Parcerias com prefeituras",
                "Serviços complementares (delivery, etc.)"
            ],
            "estrategia_diferenciacao": {
                "foco_geografico": "Cidades de 20k-100k habitantes",
                "proposta_valor": "Serviço personalizado e comprometido",
                "modelo_operacional": "Parceria real com motoristas locais"
            }
        }
        
        return json.dumps(competitive_landscape, indent=2, ensure_ascii=False)
    
    def financial_health_check(self, financial_data: str) -> str:
        """
        Avalia saúde financeira da operação.
        
        Args:
            financial_data: JSON com dados financeiros
            
        Returns:
            Diagnóstico da saúde financeira
        """
        try:
            data = json.loads(financial_data)
            
            health_check = {
                "score_saude_financeira": 0,  # 0-100
                "indicadores": {},
                "riscos_identificados": [],
                "acoes_recomendadas": []
            }
            
            # Calcular indicadores
            total_gastos = data.get("total_gastos", 0)
            media_dia = data.get("media_gastos_dia", 0)
            
            if total_gastos > 0:
                # Burn rate (queima de caixa)
                burn_rate_mensal = media_dia * 30
                health_check["indicadores"]["burn_rate_mensal"] = round(burn_rate_mensal, 2)
                
                # Eficiência de gasto
                if "corridas_concluidas" in data:
                    corridas = data["corridas_concluidas"]
                    if corridas > 0:
                        custo_por_corrida = total_gastos / corridas
                        health_check["indicadores"]["custo_aquisicao_corrida"] = round(custo_por_corrida, 2)
                        
                        if custo_por_corrida > 15:
                            health_check["riscos_identificados"].append("Alto custo de aquisição por corrida")
                            health_check["acoes_recomendadas"].append("Otimizar canais de marketing")
            
            # Score final baseado nos indicadores
            score = 70  # Base
            if len(health_check["riscos_identificados"]) == 0:
                score += 20
            elif len(health_check["riscos_identificados"]) > 2:
                score -= 30
            
            health_check["score_saude_financeira"] = max(0, min(100, score))
            
            return json.dumps(health_check, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return f"Erro na análise financeira: {str(e)}"
