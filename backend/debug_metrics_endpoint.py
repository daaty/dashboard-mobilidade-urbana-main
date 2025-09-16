#!/usr/bin/env python3
"""
Script para debugar o endpoint de métricas e ver exatamente o que está sendo retornado
"""

import requests
import json

def debug_metrics_endpoint():
    """Debug do endpoint de métricas"""

    print("🔧 DEBUG ENDPOINT DE MÉTRICAS")
    print("=" * 50)

    base_url = "http://localhost:8000"
    metrics_url = f"{base_url}/api/metrics/overview"

    try:
        print("📡 Fazendo request para /api/metrics/overview...")
        response = requests.get(metrics_url, params={"periodo": "30d"})
        data = response.json()

        print("✅ Response recebida!")
        print(f"Status Code: {response.status_code}")
        print()

        # Verificar se as chaves principais existem
        print("🔍 VERIFICAÇÃO DAS CHAVES PRINCIPAIS:")
        print("-" * 40)

        expected_keys = [
            "metricas_principais",
            "concluidas",  # <-- Esta pode estar faltando!
            "canceladas",  # <-- Esta pode estar faltando!
            "perdidas"     # <-- Esta pode estar faltando!
        ]

        for key in expected_keys:
            if key in data:
                if key == "metricas_principais":
                    print(f"✅ {key}: {len(data[key])} campos")
                else:
                    print(f"✅ {key}: {len(data[key])} itens")
            else:
                print(f"❌ {key}: CHAVE AUSENTE!")

        print()

        # Mostrar estrutura geral
        print("📋 ESTRUTURA GERAL DO RESPONSE:")
        print("-" * 40)
        for key in sorted(data.keys()):
            if isinstance(data[key], list):
                print(f"  {key}: lista com {len(data[key])} itens")
            elif isinstance(data[key], dict):
                print(f"  {key}: dicionário com {len(data[key])} campos")
            else:
                print(f"  {key}: {type(data[key]).__name__}")

        print()

        # Verificar métricas principais
        if "metricas_principais" in data:
            print("📊 MÉTRICAS PRINCIPAIS:")
            print("-" * 40)
            mp = data["metricas_principais"]
            for key, value in mp.items():
                print(f"  {key}: {value}")

        print()

        # Verificar se há dados nas listas esperadas
        for key in ["concluidas", "canceladas", "perdidas"]:
            if key in data:
                lista = data[key]
                print(f"📋 ANÁLISE DA LISTA '{key.upper()}':")
                print("-" * 40)
                print(f"  Total de itens: {len(lista)}")

                if lista:
                    print("  Primeiros 2 itens:")
                    for i, item in enumerate(lista[:2]):
                        print(f"    {i+1}. ID: {item.get('id_corrida', 'N/A')}, Nome: {item.get('nome', 'N/A')[:30]}...")
                else:
                    print("  ❌ LISTA VAZIA!")
                print()

        # Verificar se o problema é que as listas não estão sendo retornadas
        print("🔍 DIAGNÓSTICO:")
        print("-" * 40)

        has_concluidas = "concluidas" in data and len(data["concluidas"]) > 0
        has_canceladas = "canceladas" in data and len(data["canceladas"]) > 0
        has_perdidas = "perdidas" in data and len(data["perdidas"]) > 0

        if not has_concluidas and not has_canceladas and not has_perdidas:
            print("❌ PROBLEMA IDENTIFICADO:")
            print("   As listas 'concluidas', 'canceladas' e 'perdidas' estão vazias ou ausentes!")
            print("   Isso explica por que o dashboard mostra 0 corridas nos KPIs.")
            print()
            print("🔧 POSSÍVEIS CAUSAS:")
            print("   1. As listas não estão sendo incluídas no return do endpoint")
            print("   2. Não há dados no banco que atendam aos filtros")
            print("   3. Problema na extração de datas dos registros")
            print("   4. Problema na query do banco de dados")
        else:
            print("✅ Pelo menos uma das listas tem dados")

        print()
        print("=" * 50)
        print("🏁 DEBUG CONCLUÍDO")

    except Exception as e:
        print(f"❌ ERRO no debug: {str(e)}")
        print("Verifique se o servidor FastAPI está rodando na porta 8000")

if __name__ == "__main__":
    debug_metrics_endpoint()