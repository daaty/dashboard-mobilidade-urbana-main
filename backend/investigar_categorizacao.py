#!/usr/bin/env python3
"""
Script para investigar a categorização de corridas entre KPIs e Mapa de Calor
"""
import requests
import json
from datetime import datetime

def testar_categorizacao_corridas():
    """Testa e compara a categorização de corridas entre diferentes fontes"""

    print("🔍 INVESTIGANDO CATEGORIZAÇÃO DE CORRIDAS")
    print("=" * 60)

    # 1. Testar API dos KPIs
    print("\n📊 1. DADOS DOS KPIs (Google Sheets):")
    try:
        response = requests.get('http://localhost:8000/api/metrics/overview?periodo=6m', timeout=10)
        if response.status_code == 200:
            kpis_data = response.json()
            metricas = kpis_data.get('metricas_principais', {})
            distribuicao = kpis_data.get('distribuicao_status', [])

            # Extrair dados das métricas principais
            kpis_concluidas = metricas.get('corridas_concluidas', 0)
            kpis_canceladas = metricas.get('corridas_canceladas', 0)
            kpis_perdidas = metricas.get('corridas_perdidas', 0)
            total_kpis = kpis_concluidas + kpis_canceladas + kpis_perdidas

            print(f"   Total: {total_kpis}")
            print(f"   Concluídas: {kpis_concluidas}")
            print(f"   Canceladas: {kpis_canceladas}")
            print(f"   Perdidas: {kpis_perdidas}")

            # Mostrar distribuição por status
            print("   Distribuição por status:")
            for item in distribuicao:
                status = item.get('status', '')
                quantidade = item.get('quantidade', 0)
                print(f"     {status.title()}: {quantidade}")

        else:
            print(f"   ❌ Erro na API dos KPIs: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao conectar com API dos KPIs: {e}")

    # 2. Testar API do Mapa de Calor
    print("\n🗺️  2. DADOS DO MAPA DE CALOR (PostgreSQL):")
    try:
        response = requests.get('http://localhost:8000/api/mapa-calor-problemas?periodo=6m', timeout=10)
        if response.status_code == 200:
            mapa_data = response.json()
            pontos = mapa_data.get('pontos', [])

            # Contar por status
            status_count = {}
            for ponto in pontos:
                status = ponto.get('status', 'desconhecido')
                status_count[status] = status_count.get(status, 0) + 1

            print(f"   Total pontos: {len(pontos)}")
            for status, count in status_count.items():
                print(f"   {status.title()}: {count}")

            # Mostrar alguns exemplos
            print("\n   📋 EXEMPLOS DE CATEGORIZAÇÃO:")
            for i, ponto in enumerate(pontos[:5]):
                print(f"     {i+1}. Status: {ponto.get('status', 'N/A')} - Endereço: {ponto.get('endereco', 'N/A')[:50]}...")

        else:
            print(f"   ❌ Erro na API do mapa: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao conectar com API do mapa: {e}")

    # 3. Comparação detalhada
    print("\n⚖️  3. COMPARAÇÃO DETALHADA:")
    if 'kpis_concluidas' in locals() and 'mapa_data' in locals():
        print(f"   CONCLUÍDAS - KPIs: {kpis_concluidas} | Mapa: {status_count.get('concluida', 0)}")
        print(f"   CANCELADAS - KPIs: {kpis_canceladas} | Mapa: {status_count.get('cancelada', 0)} | Diferença: {abs(kpis_canceladas - status_count.get('cancelada', 0))}")
        print(f"   PERDIDAS - KPIs: {kpis_perdidas} | Mapa: {status_count.get('perdida', 0)} | Diferença: {abs(kpis_perdidas - status_count.get('perdida', 0))}")

        if kpis_canceladas < status_count.get('cancelada', 0):
            print("   ⚠️  CANCELADAS: KPIs mostram MENOS que o mapa")
        if kpis_perdidas < status_count.get('perdida', 0):
            print("   ⚠️  PERDIDAS: KPIs mostram MENOS que o mapa")

    print("\n🔍 4. VERIFICAÇÃO DE POSSÍVEIS ERROS:")

    # Verificar se há corridas perdidas sendo categorizadas como canceladas
    if 'pontos' in locals():
        print("   Analisando categorização dos pontos do mapa...")

        # Verificar se algum ponto tem indícios de estar mal categorizado
        suspeitas = []
        for ponto in pontos:
            endereco = ponto.get('endereco', '').lower()
            motivo = ponto.get('motivo', '').lower() if ponto.get('motivo') else ''

            # Se é cancelada mas tem indícios de ser perdida
            if ponto.get('status') == 'cancelada':
                if 'sem motorista' in motivo or 'não encontrado' in motivo or 'missed' in endereco:
                    suspeitas.append(f"Cancelada suspeita: {motivo} - {endereco[:30]}...")

            # Se é perdida mas tem indícios de ser cancelada
            elif ponto.get('status') == 'perdida':
                if 'cancel' in endereco or 'cliente cancelou' in endereco:
                    suspeitas.append(f"Perdida suspeita: {endereco[:50]}...")

        if suspeitas:
            print("   🚨 POSSÍVEIS ERROS DE CATEGORIZAÇÃO ENCONTRADOS:")
            for suspeita in suspeitas[:10]:  # Mostrar apenas os primeiros 10
                print(f"      - {suspeita}")
        else:
            print("   ✅ Nenhuma categorização suspeita encontrada nos primeiros registros")

if __name__ == "__main__":
    testar_categorizacao_corridas()