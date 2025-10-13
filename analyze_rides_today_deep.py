"""
Script APRIMORADO para analisar CORRIDAS DE HOJE
Análise profunda da inconsistência encontrada
"""

import json
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

def analyze_endpoint(name, url, params=None):
    """Analisa um endpoint em detalhes"""
    print(f"\n{'='*80}")
    print(f"🔍 ANALISANDO: {name}")
    print(f"📍 URL: {url}")
    if params:
        print(f"📋 Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erro HTTP {response.status_code}")
            return None
        
        data = response.json()
        
        # Análise profunda
        analysis = {
            "name": name,
            "url": url,
            "params": params,
            "data_type": type(data).__name__,
        }
        
        if isinstance(data, list):
            analysis["count"] = len(data)
            analysis["structure"] = "Array direto de objetos"
            
            if len(data) > 0:
                first_item = data[0]
                analysis["item_keys"] = list(first_item.keys()) if isinstance(first_item, dict) else str(type(first_item))
                
                # Para Passengers List, vamos somar total_rides de cada passageiro
                if "total_rides" in str(first_item):
                    total_rides_sum = sum(item.get("total_rides", 0) for item in data if isinstance(item, dict))
                    analysis["total_rides_sum"] = total_rides_sum
                    analysis["interpretation"] = f"{len(data)} passageiros com {total_rides_sum} corridas no total"
        
        elif isinstance(data, dict):
            analysis["keys"] = list(data.keys())
            
            # Verificar se tem summary
            if "summary" in data:
                summary = data["summary"]
                analysis["summary"] = summary
                if isinstance(summary, dict) and "total_rides" in summary:
                    analysis["count"] = summary["total_rides"]
                    analysis["structure"] = "Dict com summary.total_rides"
            
            # Verificar se tem array de dados em algum lugar
            for key, value in data.items():
                if isinstance(value, list):
                    analysis[f"array_{key}_length"] = len(value)
                    
                    # Se for um array de corridas
                    if len(value) > 0 and isinstance(value[0], dict):
                        first_item = value[0]
                        if any(field in first_item for field in ["ride_id", "corrida_id", "id", "created_at"]):
                            analysis["rides_array_key"] = key
                            analysis["rides_count_from_array"] = len(value)
                            analysis["structure"] = f"Dict com array de corridas em '{key}'"
            
            # Buscar campos de contagem
            for key in ["total_rides", "total_corridas", "count", "total"]:
                if key in data:
                    analysis[f"field_{key}"] = data[key]
        
        # Imprimir análise
        print(f"\n📊 ESTRUTURA: {analysis.get('structure', 'Desconhecida')}")
        print(f"📈 TIPO: {analysis['data_type']}")
        
        if "count" in analysis:
            print(f"✅ CORRIDAS HOJE: {analysis['count']}")
        
        if "total_rides_sum" in analysis:
            print(f"📊 Soma total_rides dos passageiros: {analysis['total_rides_sum']}")
            print(f"⚠️  ATENÇÃO: Este endpoint retorna {analysis['count']} passageiros, não corridas!")
        
        if "rides_count_from_array" in analysis:
            print(f"📋 Array '{analysis['rides_array_key']}' tem {analysis['rides_count_from_array']} items")
        
        # Salvar análise completa
        filename = f"analysis_{name.replace(' ', '_').replace('/', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        return analysis
        
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return None

def main():
    print("="*80)
    print("🚀 ANÁLISE PROFUNDA - CORRIDAS DE HOJE (2025-10-12)")
    print("="*80)
    
    analyses = []
    
    # 1. Passengers Analytics
    result = analyze_endpoint(
        "Passengers Analytics",
        f"{BASE_URL}/api/passengers/analytics",
        {"period": "today", "city": "all"}
    )
    analyses.append(result)
    
    # 2. Passengers KPIs
    result = analyze_endpoint(
        "Passengers KPIs",
        f"{BASE_URL}/api/passengers/kpis",
        {"period": "today", "city": "all"}
    )
    analyses.append(result)
    
    # 3. Passengers List
    result = analyze_endpoint(
        "Passengers List",
        f"{BASE_URL}/api/passengers/list",
        {"period": "today", "city": "all", "limit": 1000}
    )
    analyses.append(result)
    
    # 4. Metrics Overview
    result = analyze_endpoint(
        "Metrics Overview",
        f"{BASE_URL}/api/metrics/overview",
        {"periodo": "hoje"}
    )
    analyses.append(result)
    
    # 5. Performance Analytics Detailed Metrics
    result = analyze_endpoint(
        "Performance Analytics Detailed",
        f"{BASE_URL}/api/analytics/performance/detailed-metrics",
        {"period": "today", "city": "all"}
    )
    analyses.append(result)
    
    # 6. Drivers KPIs
    result = analyze_endpoint(
        "Drivers KPIs",
        f"{BASE_URL}/api/drivers/kpis",
        {"period": "today", "city": "all"}
    )
    analyses.append(result)
    
    # RELATÓRIO FINAL
    print("\n" + "="*80)
    print("📊 RELATÓRIO CONSOLIDADO - CORRIDAS DE HOJE")
    print("="*80)
    
    valid_analyses = [a for a in analyses if a is not None]
    
    print(f"\n{'Endpoint':<40} | {'Corridas':>10} | {'Observação':<30}")
    print("-"*85)
    
    for analysis in valid_analyses:
        name = analysis['name']
        count = analysis.get('count', 'N/A')
        obs = ""
        
        if "total_rides_sum" in analysis:
            obs = f"({analysis['total_rides_sum']} total rides)"
        elif "rides_count_from_array" in analysis:
            obs = f"({analysis['rides_count_from_array']} no array)"
        
        print(f"{name:<40} | {str(count):>10} | {obs:<30}")
    
    # Identificar o endpoint correto
    print("\n" + "="*80)
    print("🎯 CONCLUSÃO")
    print("="*80)
    
    rides_counts = {}
    for analysis in valid_analyses:
        if "count" in analysis and analysis["count"] != "N/A":
            # Ignorar endpoints que retornam lista de passageiros
            if "total_rides_sum" not in analysis:
                rides_counts[analysis["name"]] = analysis["count"]
    
    if rides_counts:
        print(f"\n📈 Valores de corridas encontrados: {set(rides_counts.values())}")
        print(f"\nDetalhes:")
        for name, count in rides_counts.items():
            print(f"  • {name}: {count} corridas")
    
    # Salvar relatório final
    final_report = {
        "timestamp": datetime.now().isoformat(),
        "date": "2025-10-12",
        "analyses": valid_analyses,
        "rides_counts": rides_counts
    }
    
    with open("final_rides_analysis_report.json", 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Relatório final salvo em: final_rides_analysis_report.json")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
