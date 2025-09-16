import requests
import json

# Testar API com filtro de período de 6 meses
url = 'http://localhost:8000/api/mapa-calor-problemas?periodo=6m'
print('🌐 Testando API com 6 meses:', url)

try:
    response = requests.get(url)
    data = response.json()

    print('📊 Estatísticas da API (6m):')
    if 'estatisticas' in data:
        stats = data['estatisticas']
        print(f'  Total registros processados: {stats.get("total_registros_processados", 0)}')
        print(f'  Pontos geocodificados: {stats.get("pontos_geocodificados", 0)}')
        print(f'  Período: {stats.get("periodo", "N/A")}')
        print(f'  Data início: {stats.get("data_inicio", "N/A")}')
        print(f'  Data fim: {stats.get("data_fim", "N/A")}')

    pontos = data.get('pontos', [])
    print(f'  Total pontos retornados: {len(pontos)}')

    # Contar por status
    status_count = {}
    for ponto in pontos:
        status = ponto.get('status', 'desconhecido')
        status_count[status] = status_count.get(status, 0) + 1

    print('  Distribuição por status:')
    for status, count in status_count.items():
        print(f'    {status}: {count}')

    print('\n' + '='*50)
    print('🔍 COMPARAÇÃO COM O PROBLEMA REPORTADO:')
    print('KPIs (6m): 146 concluídas + 15 canceladas + 90 perdidas = 251 total')
    print(f'Mapa (6m): {status_count.get("concluida", 0)} concluídas + {status_count.get("cancelada", 0)} canceladas + {status_count.get("perdida", 0)} perdidas = {len(pontos)} total')
    print(f'Diferença: {len(pontos) - 251} corridas')

except Exception as e:
    print('❌ Erro ao testar API:', str(e))