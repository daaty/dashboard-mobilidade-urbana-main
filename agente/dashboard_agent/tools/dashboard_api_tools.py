"""
🎯 FERRAMENTAS PARA CONSUMIR API DO DASHBOARD DE MOBILIDADE URBANA
Tools para análise de dados de corridas, motoristas, metas e insights financeiros
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from agno.tools import Toolkit
from agno.utils.log import logger


class DashboardAPITools(Toolkit):
    """Ferramentas para consumir todas as APIs do Dashboard de Mobilidade Urbana"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        **kwargs
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # 🎯 CORREÇÃO CRÍTICA: Adicionar métodos explicitamente à lista de tools
        tools = [
            self.get_rides_overview,
            self.get_rides_by_city,
            self.get_drivers_overview,
            self.get_drivers_by_city,
            self.get_financial_overview,
            self.get_strategic_goals,
            self.get_cities_data,
            self.analyze_ride_patterns,
            self.get_driver_performance_metrics,
            self.calculate_roi_metrics
        ]
        
        super().__init__(name="dashboard_api_tools", tools=tools, **kwargs)
        print(f"✅ [INIT] DashboardAPITools inicializado com {len(tools)} ferramentas")
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Método auxiliar para fazer requisições HTTP"""
        try:
            url = f"{self.base_url}{endpoint}"
            print(f"🔗 [TOOL] Fazendo requisição: {method} {url}")
            if kwargs.get('params'):
                print(f"📊 [TOOL] Parâmetros: {kwargs['params']}")
            
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            print(f"✅ [TOOL] Status: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            print(f"📋 [TOOL] Dados recebidos com {len(str(data))} caracteres")
            return data
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição {method} {endpoint}: {e}"
            print(f"❌ [TOOL] {error_msg}")
            logger.error(error_msg)
            return {"error": str(e), "success": False}
    
    # ========== ANÁLISE DE CORRIDAS ==========
    
    def get_rides_overview(self, cidade: Optional[str] = None, periodo: str = "30d") -> str:
        """
        Busca métricas gerais de corridas por cidade e período.
        
        Args:
            cidade: Nome da cidade (opcional)
            periodo: Período de análise (7d, 30d, 90d)
            
        Returns:
            JSON com métricas de corridas concluídas, canceladas, perdidas
        """
        params = {"periodo": periodo}
        if cidade:
            params["cidade"] = cidade
            
        data = self._make_request("GET", "/api/metrics/overview", params=params)
        
        if "error" in data:
            return f"Erro ao buscar dados de corridas: {data['error']}"
            
        return json.dumps({
            "metricas_principais": data.get("metricas_principais", {}),
            "evolucao": data.get("evolucao", []),
            "distribuicao_status": data.get("distribuicao_status", []),
            "atividade_recente": data.get("atividade_recente", {}),
            "periodo_analisado": periodo,
            "cidade": cidade or "Todas"
        }, indent=2, ensure_ascii=False)
    
    def get_rides_by_city(self) -> str:
        """
        Busca distribuição de corridas por cidade.
        
        Returns:
            JSON com ranking de cidades por volume de corridas
        """
        data = self._make_request("GET", "/api/metrics/rides-by-city")
        
        if "error" in data:
            return f"Erro ao buscar corridas por cidade: {data['error']}"
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    # ========== ANÁLISE DE MOTORISTAS ==========
    
    def get_drivers_overview(self, periodo: str = "30d") -> str:
        """
        Busca métricas gerais de motoristas.
        
        Args:
            periodo: Período de análise (7d, 30d, 90d) - informativo apenas
            
        Returns:
            JSON com dados de motoristas ativos, avaliações, etc.
        """
        print(f"🚗 [TOOL] get_drivers_overview() chamada com periodo={periodo}")
        print(f"🔗 [TOOL] URL base configurada: {self.base_url}")
        print(f"🤖 [TOOL] Chamada vem do framework AGNO")
        
        try:
            # API não aceita parâmetros de período, então fazemos requisição simples
            data = self._make_request("GET", "/api/drivers/overview")
            
            if "error" in data:
                error_msg = f"Erro ao buscar dados de motoristas: {data['error']}"
                print(f"❌ [TOOL] {error_msg}")
                return error_msg
            
            print(f"✅ [TOOL] Dados de motoristas obtidos: {data.get('active_drivers', 'N/A')} ativos")
            result = json.dumps(data, indent=2, ensure_ascii=False)
            print(f"📤 [TOOL] Retornando dados de motoristas ({len(result)} caracteres)")
            return result
            
        except Exception as e:
            error_msg = f"❌ [TOOL] EXCEÇÃO em get_drivers_overview(): {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_drivers_by_city(self, cidade: str) -> str:
        """
        Busca motoristas específicos de uma cidade.
        
        Args:
            cidade: Nome da cidade
            
        Returns:
            JSON com motoristas da cidade especificada
        """
        params = {"cidade": cidade}
        data = self._make_request("GET", "/api/drivers/by-city", params=params)
        
        if "error" in data:
            return f"Erro ao buscar motoristas de {cidade}: {data['error']}"
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    # ========== ANÁLISE FINANCEIRA ==========
    
    def get_financial_overview(self, periodo: str = "30d") -> str:
        """
        Busca métricas financeiras gerais.
        
        Args:
            periodo: Período de análise (informativo apenas)
            
        Returns:
            JSON com gastos, receitas, ROI, etc.
        """
        # Usar endpoint correto da API
        data = self._make_request("GET", "/api/financeiro/overview")
        
        if "error" in data:
            return f"Erro ao buscar dados financeiros: {data['error']}"
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def get_financial_by_category(self) -> str:
        """
        Busca gastos categorizados.
        
        Returns:
            JSON com distribuição de gastos por categoria
        """
        # Endpoint não disponível - retornar dados limitados
        return json.dumps({
            "aviso": "Endpoint de categorias financeiras não disponível",
            "dados_disponiveis": "Use get_financial_overview() para dados gerais",
            "sugestao": "Implementar endpoint /api/financeiro/categorias na API"
        }, indent=2, ensure_ascii=False)
    
    # ========== METAS ESTRATÉGICAS ==========
    
    def get_strategic_goals(self) -> str:
        """
        Busca metas estratégicas e progresso.
        
        Returns:
            JSON com metas progressivas e fases de planejamento
        """
        data = self._make_request("GET", "/api/metas-estrategicas/dashboard")
        
        if "error" in data:
            return f"Erro ao buscar metas estratégicas: {data['error']}"
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def get_progressive_goals(self) -> str:
        """
        Busca metas progressivas por cidade.
        
        Returns:
            JSON com metas de corridas, motoristas e receita por cidade
        """
        data = self._make_request("GET", "/api/metas-estrategicas/metas-progressivas")
        
        if "error" in data:
            return f"Erro ao buscar metas progressivas: {data['error']}"
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def get_planning_phases(self) -> str:
        """
        Busca fases de planejamento estratégico.
        
        Returns:
            JSON com fases, cronograma e orçamentos
        """
        data = self._make_request("GET", "/api/metas-estrategicas/fases-planejamento")
        
        if "error" in data:
            return f"Erro ao buscar fases de planejamento: {data['error']}"
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    # ========== CAMPANHAS E CIDADES ==========
    
    def get_campaigns(self) -> str:
        """
        Busca campanhas de marketing.
        
        Returns:
            JSON com campanhas ativas por cidade
        """
        # Endpoint com erro 500 - retornar dados limitados
        return json.dumps({
            "aviso": "Endpoint de campanhas temporariamente indisponível (erro 500)",
            "dados_disponiveis": "Use get_cities_data() para dados de cidades",
            "sugestao": "Verificar implementação do endpoint /api/campanhas"
        }, indent=2, ensure_ascii=False)
    
    def get_cities_data(self) -> str:
        """
        Busca dados demográficos das cidades.
        
        Returns:
            JSON com população, público-alvo e penetração de mercado
        """
        data = self._make_request("GET", "/api/cidades")
        
        if "error" in data:
            return f"Erro ao buscar dados das cidades: {data['error']}"
            
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    # ========== ANÁLISE COMPARATIVA ==========
    
    def compare_cities_performance(self, cidades: List[str]) -> str:
        """
        Compara performance entre cidades específicas.
        
        Args:
            cidades: Lista de nomes das cidades para comparar
            
        Returns:
            Análise comparativa detalhada
        """
        results = {}
        
        for cidade in cidades:
            # Buscar dados de corridas por cidade
            rides_data = self._make_request("GET", "/api/metrics/overview", params={"cidade": cidade})
            drivers_data = self._make_request("GET", "/api/drivers/by-city", params={"cidade": cidade})
            
            results[cidade] = {
                "corridas": rides_data.get("metricas_principais", {}),
                "motoristas": drivers_data
            }
        
        return json.dumps({
            "comparacao_cidades": results,
            "cidades_analisadas": cidades,
            "data_analise": datetime.now().isoformat()
        }, indent=2, ensure_ascii=False)
    
    def get_market_penetration_analysis(self) -> str:
        """
        Análise de penetração de mercado por cidade.
        
        Returns:
            JSON com análise de penetração e potencial de crescimento
        """
        # Combinar dados de cidades e métricas de corridas
        cities_data = self._make_request("GET", "/api/cidades")
        overview_data = self._make_request("GET", "/api/metrics/overview")
        
        if "error" in cities_data or "error" in overview_data:
            return "Erro ao buscar dados para análise de penetração"
        
        analysis = {
            "penetracao_mercado": cities_data,
            "metricas_atuais": overview_data,
            "recomendacoes": "Análise de penetração combinada com métricas operacionais"
        }
        
        return json.dumps(analysis, indent=2, ensure_ascii=False)
