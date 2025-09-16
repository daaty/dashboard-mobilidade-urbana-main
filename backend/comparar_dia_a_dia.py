#!/usr/bin/env python3
"""
Comparação dia a dia entre os endpoints
"""
import requests
from collections import defaultdict

def comparar_dia_a_dia():
    """Compara os dados dia a dia entre KPIs e Mapa"""

    print("📊 COMPARAÇÃO DIA A DIA")
    print("=" * 50)

    try:
        # Buscar dados dos KPIs
        response_kpis = requests.get('http://localhost:8000/api/metrics/overview?periodo=6m', timeout=10)
        kpis_data = response_kpis.json()
        evolucao_kpis = kpis_data.get('evolucao', [])

        # Organizar por data
        kpis_por_dia = {}
        for dia in evolucao_kpis:
            data = dia['data']
            total = dia['concluidas'] + dia['canceladas'] + dia['perdidas']
            kpis_por_dia[data] = {
                'total': total,
                'concluidas': dia['concluidas'],
                'canceladas': dia['canceladas'],
                'perdidas': dia['perdidas']
            }

        # Buscar dados do mapa
        response_mapa = requests.get('http://localhost:8000/api/mapa-calor-problemas?periodo=6m', timeout=10)
        mapa_data = response_mapa.json()
        pontos = mapa_data.get('pontos', [])

        # Organizar pontos do mapa por data
        mapa_por_dia = defaultdict(lambda: {'total': 0, 'concluidas': 0, 'canceladas': 0, 'perdidas': 0})

        for ponto in pontos:
            if ponto.get('data'):
                try:
                    data_str = ponto['data'][:10]  # YYYY-MM-DD
                    status = ponto.get('status', 'desconhecido')
                    mapa_por_dia[data_str]['total'] += 1

                    if status == 'concluida':
                        mapa_por_dia[data_str]['concluidas'] += 1
                    elif status == 'cancelada':
                        mapa_por_dia[data_str]['canceladas'] += 1
                    elif status == 'perdida':
                        mapa_por_dia[data_str]['perdidas'] += 1
                except:
                    pass

        # Comparar dias com dados
        todos_dias = set(kpis_por_dia.keys()) | set(mapa_por_dia.keys())
        dias_ordenados = sorted(todos_dias, reverse=True)  # Mais recentes primeiro

        print(f"📅 Total de dias analisados: {len(todos_dias)}")
        print(f"📈 KPIs tem dados em: {len(kpis_por_dia)} dias")
        print(f"🗺️ Mapa tem dados em: {len(mapa_por_dia)} dias")
        print()

        # Mostrar diferenças significativas
        print("🔍 DIAS COM DIFERENÇAS SIGNIFICATIVAS:")
        print("-" * 80)

        dias_com_diferenca = []
        for dia in dias_ordenados[:30]:  # Últimos 30 dias
            kpis = kpis_por_dia.get(dia, {'total': 0, 'concluidas': 0, 'canceladas': 0, 'perdidas': 0})
            mapa = mapa_por_dia.get(dia, {'total': 0, 'concluidas': 0, 'canceladas': 0, 'perdidas': 0})

            diff_total = abs(kpis['total'] - mapa['total'])
            diff_canceladas = abs(kpis['canceladas'] - mapa['canceladas'])
            diff_perdidas = abs(kpis['perdidas'] - mapa['perdidas'])

            if diff_total > 0 or diff_canceladas > 5 or diff_perdidas > 5:
                dias_com_diferenca.append({
                    'dia': dia,
                    'kpis_total': kpis['total'],
                    'mapa_total': mapa['total'],
                    'diff_total': diff_total,
                    'kpis_canceladas': kpis['canceladas'],
                    'mapa_canceladas': mapa['canceladas'],
                    'diff_canceladas': diff_canceladas,
                    'kpis_perdidas': kpis['perdidas'],
                    'mapa_perdidas': mapa['perdidas'],
                    'diff_perdidas': diff_perdidas
                })

        # Ordenar por diferença total (maior primeiro)
        dias_com_diferenca.sort(key=lambda x: x['diff_total'], reverse=True)

        for item in dias_com_diferenca[:10]:  # Top 10 diferenças
            print(f"📅 {item['dia']}:")
            print(f"   Total - KPIs: {item['kpis_total']} | Mapa: {item['mapa_total']} | Dif: {item['diff_total']}")
            print(f"   Canceladas - KPIs: {item['kpis_canceladas']} | Mapa: {item['mapa_canceladas']} | Dif: {item['diff_canceladas']}")
            print(f"   Perdidas - KPIs: {item['kpis_perdidas']} | Mapa: {item['mapa_perdidas']} | Dif: {item['diff_perdidas']}")
            print()

        # Resumo das diferenças
        total_diff_canceladas = sum(item['diff_canceladas'] for item in dias_com_diferenca)
        total_diff_perdidas = sum(item['diff_perdidas'] for item in dias_com_diferenca)

        print("📋 RESUMO DAS DIFERENÇAS:")
        print(f"   🔴 Diferença total em canceladas: {total_diff_canceladas}")
        print(f"   🟡 Diferença total em perdidas: {total_diff_perdidas}")
        print(f"   📊 Dias com diferenças: {len(dias_com_diferenca)}")

    except Exception as e:
        print(f"❌ Erro na comparação: {e}")

if __name__ == "__main__":
    comparar_dia_a_dia()