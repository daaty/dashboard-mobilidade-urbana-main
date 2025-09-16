import requests
import json

def test_endpoint():
    try:
        response = requests.get('http://localhost:8000/api/metrics/overview?periodo=hoje', timeout=10)
        print(f'Status: {response.status_code}')
        data = response.json()
        print('Resposta:')
        print(f'Métricas principais: {data.get("metricas_principais")}')
        print(f'Atividade recente - Concluídas: {len(data.get("atividade_recente", {}).get("concluidas", []))}')
        print(f'Atividade recente - Canceladas: {len(data.get("atividade_recente", {}).get("canceladas", []))}')
        print(f'Atividade recente - Perdidas: {len(data.get("atividade_recente", {}).get("perdidas", []))}')

        # Verificar se há dados nas métricas principais
        metricas = data.get("metricas_principais", {})
        if all(v == 0 for v in metricas.values() if isinstance(v, (int, float))):
            print('AVISO: Todas as métricas estão zeradas!')

        # Examinar atividade recente
        atividade = data.get("atividade_recente", {})
        print('\nDetalhes da atividade recente:')
        for tipo, items in atividade.items():
            print(f'{tipo}: {len(items)} items')
            if items:
                print(f'  Primeiro item: {items[0]}')

    except Exception as e:
        print(f'Erro: {e}')

if __name__ == "__main__":
    test_endpoint()