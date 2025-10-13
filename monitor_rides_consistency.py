"""
🔍 MONITOR DE CONSISTÊNCIA DE CORRIDAS
Script para monitoramento contínuo da consistência de dados entre endpoints

Uso:
  python monitor_rides_consistency.py           # Verifica hoje
  python monitor_rides_consistency.py --period 7d  # Verifica últimos 7 dias
"""

import requests
import json
from datetime import datetime
import argparse

BASE_URL = "http://localhost:8000"

def get_rides_from_metrics(periodo="hoje"):
    """Obtém contagem CORRETA de corridas do endpoint principal"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/metrics/overview",
            params={"periodo": periodo},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            concluidas = len(data.get('concluidas', []))
            canceladas = len(data.get('canceladas', []))
            perdidas = len(data.get('perdidas', []))
            return {
                "concluidas": concluidas,
                "canceladas": canceladas,
                "perdidas": perdidas,
                "total": concluidas + canceladas + perdidas,
                "status": "OK"
            }
        return {"status": "ERROR", "code": resp.status_code}
    except Exception as e:
        return {"status": "EXCEPTION", "error": str(e)}

def get_rides_from_passengers(period="today"):
    """Obtém contagem de corridas do endpoint de passageiros"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/passengers/analytics",
            params={"period": period, "city": "all"},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            summary = data.get("summary", {})
            return {
                "total": summary.get("total_rides", 0),
                "revenue": summary.get("total_revenue", 0),
                "status": "OK",
                "note": "Apenas corridas de novos passageiros"
            }
        return {"status": "ERROR", "code": resp.status_code}
    except Exception as e:
        return {"status": "EXCEPTION", "error": str(e)}

def check_consistency():
    """Verifica consistência entre endpoints"""
    print("="*80)
    print("🔍 MONITOR DE CONSISTÊNCIA DE CORRIDAS")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    # 1. Endpoint principal (fonte da verdade)
    print("📊 Verificando endpoint principal...")
    metrics = get_rides_from_metrics("hoje")
    
    if metrics["status"] == "OK":
        print(f"   ✅ Metrics Overview: {metrics['total']} corridas")
        print(f"      • Concluídas: {metrics['concluidas']}")
        print(f"      • Canceladas: {metrics['canceladas']}")
        print(f"      • Perdidas: {metrics['perdidas']}")
    else:
        print(f"   ❌ Erro ao acessar Metrics Overview: {metrics}")
        return
    
    print()
    
    # 2. Endpoint de passageiros
    print("👥 Verificando endpoint de passageiros...")
    passengers = get_rides_from_passengers("today")
    
    if passengers["status"] == "OK":
        print(f"   ✅ Passengers Analytics: {passengers['total']} corridas")
        print(f"      💰 Receita: R$ {passengers['revenue']:.2f}")
        print(f"      ℹ️  {passengers['note']}")
    else:
        print(f"   ❌ Erro: {passengers}")
    
    print()
    
    # 3. Análise de consistência
    print("="*80)
    print("🎯 ANÁLISE DE CONSISTÊNCIA")
    print("="*80)
    print()
    
    if metrics["status"] == "OK" and passengers["status"] == "OK":
        diff = metrics["total"] - passengers["total"]
        
        if diff == 0:
            print("   ✅ CONSISTENTE! Ambos os endpoints reportam o mesmo número.")
        else:
            print(f"   ⚠️  INCONSISTÊNCIA DETECTADA!")
            print(f"   • Metrics Overview: {metrics['total']} corridas")
            print(f"   • Passengers Analytics: {passengers['total']} corridas")
            print(f"   • Diferença: {abs(diff)} corridas")
            print()
            print("   💡 Explicação:")
            print("   Passengers Analytics conta apenas corridas de NOVOS passageiros,")
            print("   enquanto Metrics Overview conta TODAS as corridas do período.")
    
    print()
    print("="*80)
    print("✨ Verificação concluída!")
    print("="*80)
    
    # Retornar dados para possível uso em CI/CD
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics_total": metrics.get("total", 0) if metrics["status"] == "OK" else None,
        "passengers_total": passengers.get("total", 0) if passengers["status"] == "OK" else None,
        "is_consistent": metrics.get("total") == passengers.get("total") if metrics["status"] == "OK" and passengers["status"] == "OK" else False
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor de consistência de corridas')
    parser.add_argument('--period', default='hoje', help='Período para análise (hoje, 7d, 30d, etc)')
    parser.add_argument('--save', action='store_true', help='Salvar resultado em JSON')
    
    args = parser.parse_args()
    
    result = check_consistency()
    
    if args.save:
        filename = f"consistency_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultado salvo em: {filename}")
