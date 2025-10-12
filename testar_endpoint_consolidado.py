#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do endpoint consolidado após limpeza
"""

import requests
import json

print("="*80)
print("🧪 TESTE: Endpoint /api/metas-estrategicas/consolidado/3")
print("="*80 + "\n")

r = requests.get('http://localhost:8000/api/metas-estrategicas/consolidado/3')

if r.status_code == 200:
    data = r.json()
    
    print(f"✅ Status: {r.status_code}")
    print(f"✅ Cidade: {data['cidade_nome']}")
    print(f"✅ Total períodos: {data['total_periodos']}\n")
    
    print("📊 Metas por período:")
    print("-" * 80)
    
    for meta in data['metas']:
        print(f"\n🔹 {meta['periodo_descricao'].upper()} (ID: {meta['id']})")
        print(f"   Metas: {meta['metas']['corridas']} corridas | {meta['metas']['motoristas']} motoristas | R$ {meta['metas']['receita']:.2f}")
        print(f"   Resultados: {meta['resultados']['corridas']} corridas | {meta['resultados']['motoristas']} motoristas | R$ {meta['resultados']['receita']:.2f}")
        print(f"   Progresso: Corridas {meta['progresso']['corridas']}% | Receita {meta['progresso']['receita']}% | Motoristas {meta['progresso']['motoristas']}%")
        print(f"   Satisfação: {meta['resultados']['satisfacao']:.2f}/5.00 | Cancelamento: {meta['resultados']['taxa_cancelamento']:.2f}%")
    
    print("\n" + "="*80)
    print("✅ ENDPOINT FUNCIONANDO CORRETAMENTE!")
    print("="*80)
else:
    print(f"❌ Erro: Status {r.status_code}")
    print(r.text)
