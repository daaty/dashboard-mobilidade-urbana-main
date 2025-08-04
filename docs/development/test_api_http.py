import requests
import json

# Testar a API Financeira via HTTP
def test_api_financeira():
    base_url = "http://localhost:8000"
    
    # Teste para diferentes períodos
    periodos = ['hoje', '7d', '30d', '6m']
    
    for periodo in periodos:
        print(f"\n=== API Financeira - {periodo} ===")
        try:
            response = requests.get(f"{base_url}/api/financeiro/overview?period={periodo}")
            if response.status_code == 200:
                data = response.json()
                print(f"Total de gastos: R$ {data.get('total_gastos', 0):.2f}")
                print(f"Total de transações: {data.get('total_transacoes', 0)}")
                print(f"Taxa de documentação: {data.get('taxa_documentacao', 0):.1f}%")
                print(f"Média diária: R$ {data.get('media_diaria', 0):.2f}")
                print(f"Projeção mensal: R$ {data.get('projecao_mensal', 0):.2f}")
                
                categorias = data.get('gastos_por_categoria', {})
                if categorias:
                    print("Categorias:")
                    for cat, valor in categorias.items():
                        print(f"  {cat}: R$ {valor:.2f}")
            else:
                print(f"Erro {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_api_financeira()
