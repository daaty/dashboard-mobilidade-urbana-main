"""
Script para testar consistência de dados de corridas entre diferentes endpoints
Foco: Corridas de HOJE
Data: 2025-10-12
"""

import requests
import json
from datetime import datetime, date
from typing import Dict, List, Any
import sys

# Configuração
BASE_URL = "http://localhost:8000"
TODAY = date.today().isoformat()  # 2025-10-12

class RidesEndpointTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = {}
        self.errors = []
        
    def test_endpoint(self, name: str, url: str, params: Dict = None) -> Dict[str, Any]:
        """Testa um endpoint e extrai informações sobre corridas"""
        try:
            print(f"\n{'='*80}")
            print(f"🔍 Testando: {name}")
            print(f"📍 URL: {url}")
            if params:
                print(f"📋 Params: {params}")
            
            response = requests.get(url, params=params, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Salvar resposta completa para análise
                filename = f"response_{name.replace(' ', '_').replace('/', '_')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"💾 Resposta salva em: {filename}")
                
                # Analisar estrutura
                rides_count = self._extract_rides_count(data, name)
                
                result = {
                    "status": "SUCCESS",
                    "status_code": response.status_code,
                    "rides_count": rides_count,
                    "data_structure": self._analyze_structure(data),
                    "response_file": filename
                }
                
                print(f"✅ Total de Corridas: {rides_count}")
                
                return result
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                print(f"❌ Erro: {error_msg}")
                return {
                    "status": "ERROR",
                    "status_code": response.status_code,
                    "error": error_msg
                }
                
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")
            return {
                "status": "EXCEPTION",
                "error": str(e)
            }
    
    def _extract_rides_count(self, data: Any, endpoint_name: str) -> int:
        """Extrai o número de corridas de diferentes estruturas de resposta"""
        
        # Caso 1: Lista direta de corridas
        if isinstance(data, list):
            return len(data)
        
        # Caso 2: Dicionário com key 'rides' ou 'corridas'
        if isinstance(data, dict):
            # Tentar diferentes keys comuns
            for key in ['rides', 'corridas', 'data', 'results', 'items']:
                if key in data and isinstance(data[key], list):
                    return len(data[key])
            
            # Verificar se tem 'total' ou 'count' direto
            for key in ['total', 'count', 'total_rides', 'total_corridas']:
                if key in data:
                    return int(data[key])
            
            # Verificar estruturas aninhadas
            if 'metrics' in data and isinstance(data['metrics'], dict):
                if 'total_rides' in data['metrics']:
                    return int(data['metrics']['total_rides'])
                if 'corridas' in data['metrics']:
                    return int(data['metrics']['corridas'])
            
            # Para analytics/performance que podem ter dados agregados
            if 'summary' in data and isinstance(data['summary'], dict):
                if 'total_rides' in data['summary']:
                    return int(data['summary']['total_rides'])
            
            # Se tiver um array em algum lugar, pegar o primeiro que encontrar
            for value in data.values():
                if isinstance(value, list):
                    print(f"⚠️  Encontrado array com {len(value)} items em estrutura não padrão")
                    return len(value)
        
        print(f"⚠️  Não foi possível extrair contagem de corridas. Estrutura: {type(data)}")
        return 0
    
    def _analyze_structure(self, data: Any) -> str:
        """Analisa a estrutura dos dados"""
        if isinstance(data, list):
            if len(data) > 0:
                return f"Array[{len(data)}] - Primeiro item keys: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}"
            return f"Array[0] - vazio"
        elif isinstance(data, dict):
            return f"Dict - Keys: {list(data.keys())}"
        else:
            return f"Type: {type(data)}"
    
    def run_all_tests(self):
        """Executa testes em todos os endpoints relacionados a corridas"""
        
        print("="*80)
        print("🚀 TESTE DE CONSISTÊNCIA DE CORRIDAS - ENDPOINTS")
        print(f"📅 Data de Teste: {TODAY}")
        print(f"🌐 Base URL: {self.base_url}")
        print("="*80)
        
        # Lista de endpoints para testar
        endpoints = [
            # PASSENGERS - Analytics (Este funciona!)
            {
                "name": "Passengers - Analytics",
                "url": f"{self.base_url}/api/passengers/analytics",
                "params": {"period": "today", "city": "all"}
            },
            
            # PASSENGERS - KPIs
            {
                "name": "Passengers - KPIs",
                "url": f"{self.base_url}/api/passengers/kpis",
                "params": {"period": "today", "city": "all"}
            },
            
            # PASSENGERS - List
            {
                "name": "Passengers - List",
                "url": f"{self.base_url}/api/passengers/list",
                "params": {"period": "today", "city": "all", "limit": 1000}
            },
            
            # DRIVERS - KPIs
            {
                "name": "Drivers - KPIs",
                "url": f"{self.base_url}/api/drivers/kpis",
                "params": {"period": "today", "city": "all"}
            },
            
            # DRIVERS - Analytics (from drivers.py)
            {
                "name": "Drivers - Analytics",
                "url": f"{self.base_url}/api/drivers/analytics",
                "params": {"period": "today", "city": "all"}
            },
            
            # DRIVERS ANALYTICS - Performance Metrics
            {
                "name": "Drivers Analytics - Performance Metrics",
                "url": f"{self.base_url}/api/drivers/analytics/performance-metrics",
                "params": {"period": "today", "city": "all"}
            },
            
            # METRICS - Overview
            {
                "name": "Metrics - Overview",
                "url": f"{self.base_url}/api/metrics/overview",
                "params": {"periodo": "hoje", "cidade": None}
            },
            
            # PERFORMANCE ANALYTICS - Overview
            {
                "name": "Performance Analytics - Overview",
                "url": f"{self.base_url}/api/analytics/performance/overview",
                "params": {"period": "today", "city": "all"}
            },
            
            # PERFORMANCE ANALYTICS - Detailed Metrics
            {
                "name": "Performance Analytics - Detailed Metrics",
                "url": f"{self.base_url}/api/analytics/performance/detailed-metrics",
                "params": {"period": "today", "city": "all"}
            },
        ]
        
        # Testar cada endpoint
        for endpoint in endpoints:
            result = self.test_endpoint(
                name=endpoint["name"],
                url=endpoint["url"],
                params=endpoint.get("params")
            )
            self.results[endpoint["name"]] = result
        
        # Gerar relatório de comparação
        self.generate_comparison_report()
    
    def generate_comparison_report(self):
        """Gera relatório comparativo dos resultados"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE COMPARAÇÃO DE CORRIDAS")
        print("="*80)
        
        # Filtrar endpoints bem-sucedidos
        successful = {k: v for k, v in self.results.items() if v.get("status") == "SUCCESS"}
        
        if not successful:
            print("❌ Nenhum endpoint retornou dados com sucesso!")
            return
        
        # Tabela de resultados
        print(f"\n{'Endpoint':<40} | {'Corridas':>10} | {'Status':>10}")
        print("-" * 80)
        
        rides_counts = {}
        for name, result in self.results.items():
            status = result.get("status", "UNKNOWN")
            rides = result.get("rides_count", 0) if status == "SUCCESS" else "N/A"
            
            if status == "SUCCESS":
                rides_counts[name] = rides
            
            rides_str = str(rides) if isinstance(rides, int) else rides
            print(f"{name:<40} | {rides_str:>10} | {status:>10}")
        
        # Análise de consistência
        if rides_counts:
            print("\n" + "="*80)
            print("🔍 ANÁLISE DE CONSISTÊNCIA")
            print("="*80)
            
            values = list(rides_counts.values())
            unique_values = set(values)
            
            print(f"\n📈 Valores únicos encontrados: {sorted(unique_values)}")
            print(f"📊 Total de endpoints testados: {len(self.results)}")
            print(f"✅ Endpoints com sucesso: {len(successful)}")
            print(f"❌ Endpoints com erro: {len(self.results) - len(successful)}")
            
            if len(unique_values) == 1:
                print(f"\n✅ CONSISTENTE! Todos os endpoints retornam {values[0]} corridas")
            else:
                print(f"\n⚠️  INCONSISTÊNCIA DETECTADA!")
                print(f"\nDetalhes das diferenças:")
                for value in sorted(unique_values):
                    endpoints_with_value = [k for k, v in rides_counts.items() if v == value]
                    print(f"\n  📍 {value} corridas:")
                    for ep in endpoints_with_value:
                        print(f"     - {ep}")
                
                # Calcular diferença máxima
                max_diff = max(values) - min(values)
                print(f"\n📊 Diferença máxima: {max_diff} corridas ({min(values)} - {max(values)})")
        
        # Salvar relatório
        report = {
            "test_date": TODAY,
            "test_timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "results": self.results,
            "summary": {
                "total_endpoints": len(self.results),
                "successful": len(successful),
                "failed": len(self.results) - len(successful),
                "rides_counts": rides_counts,
                "is_consistent": len(set(rides_counts.values())) <= 1 if rides_counts else False
            }
        }
        
        report_file = f"rides_consistency_report_{TODAY}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório completo salvo em: {report_file}")

if __name__ == "__main__":
    tester = RidesEndpointTester(BASE_URL)
    tester.run_all_tests()
    
    print("\n" + "="*80)
    print("✨ Teste concluído!")
    print("="*80)
