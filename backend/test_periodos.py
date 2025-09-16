import requests
import json

def test_periodos():
    periodos = ['7d', '30d', 'hoje']

    for periodo in periodos:
        try:
            response = requests.get(f'http://localhost:8000/api/metrics/overview?periodo={periodo}', timeout=10)
            print(f'\n=== PERÍODO: {periodo} ===')
            print(f'Status: {response.status_code}')

            if response.status_code == 200:
                data = response.json()
                metricas = data.get('metricas_principais', {})
                print('Métricas principais:')
                for k, v in metricas.items():
                    print(f'  {k}: {v}')

                atividade = data.get('atividade_recente', {})
                print('Atividade recente:')
                print(f'  Concluídas: {len(atividade.get("concluidas", []))}')
                print(f'  Canceladas: {len(atividade.get("canceladas", []))}')
                print(f'  Perdidas: {len(atividade.get("perdidas", []))}')

                # Verificar se há dados
                total = sum(metricas.get(k, 0) for k in ['corridas_concluidas', 'corridas_canceladas', 'corridas_perdidas'])
                print(f'  Total de corridas: {total}')

            else:
                print(f'Erro na resposta: {response.text}')

        except Exception as e:
            print(f'Erro ao testar {periodo}: {e}')

if __name__ == "__main__":
    test_periodos()