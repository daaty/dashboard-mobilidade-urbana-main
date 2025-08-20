"""
🤖 Dashboard Agent - Agente Inteligente para Mobilidade Urbana

Este pacote contém um agente inteligente especializado em análise de dados
de mobilidade urbana, construído com o framework agnai.

Componentes principais:
- MobilityDashboardAgent: Classe principal do agente
- DashboardAPITools: Ferramentas para consumir APIs do dashboard
- BusinessAnalysisTools: Ferramentas de análise de negócio

Exemplo de uso:
    from dashboard_agent import MobilityDashboardAgent
    
    agent = MobilityDashboardAgent()
    resultado = agent.analyze_overall_performance()
"""

from .mobility_agent import MobilityDashboardAgent
from .tools.dashboard_api_tools import DashboardAPITools
from .tools.business_analysis_tools import BusinessAnalysisTools

__version__ = "1.0.0"
__author__ = "Dashboard Mobility Team"
__email__ = "team@dashboard-mobility.com"

__all__ = [
    "MobilityDashboardAgent",
    "DashboardAPITools", 
    "BusinessAnalysisTools"
]
