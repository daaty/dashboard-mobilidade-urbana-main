#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica se metas_progressivas foi atualizada com dados reais
"""

import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

load_dotenv('backend/.env.production')

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor(cursor_factory=DictCursor)

print("="*80)
print("📊 VERIFICAÇÃO: Metas Progressivas Atualizadas")
print("="*80 + "\n")

# Mapeamento de cidade_id para nome (conforme CITY_TO_ID)
CIDADE_NOMES = {
    1: "Peixoto de Azevedo",
    2: "Nova Monte Verde", 
    3: "Matupá",
    4: "Guarantã do Norte",
    5: "Nova Bandeirantes"
}

# Buscar metas COM dados reais (resultado_corridas > 0)
cursor.execute("""
    SELECT 
        mp.id,
        mp.cidade_id,
        mp.mes,
        mp.meta_corridas,
        mp.resultado_corridas,
        mp.meta_receita,
        mp.resultado_receita,
        mp.meta_motoristas,
        mp.resultado_motoristas,
        mp.resultado_usuarios_ativos,
        mp.resultado_satisfacao,
        mp.resultado_taxa_cancelamento,
        mp.updated_at
    FROM metas_progressivas mp
    WHERE mp.resultado_corridas > 0
        OR mp.resultado_motoristas > 0
        OR mp.resultado_receita > 0
    ORDER BY mp.cidade_id, mp.mes;
""")

metas_com_dados = cursor.fetchall()

if not metas_com_dados:
    print("⚠️ NENHUMA META COM DADOS REAIS ENCONTRADA!")
    print("\nVerificando últimas atualizações...")
    cursor.execute("""
        SELECT 
            mp.id,
            mp.cidade_id,
            mp.mes,
            mp.resultado_corridas,
            mp.resultado_receita,
            mp.resultado_motoristas,
            mp.updated_at
        FROM metas_progressivas mp
        ORDER BY mp.updated_at DESC
        LIMIT 10;
    """)
    ultimas = cursor.fetchall()
    for meta in ultimas:
        cidade_nome = CIDADE_NOMES.get(meta['cidade_id'], f"Cidade {meta['cidade_id']}")
        print(f"\nCidade: {cidade_nome} ({meta['mes']} meses)")
        print(f"  Resultado Corridas: {meta['resultado_corridas']}")
        print(f"  Resultado Receita: R$ {meta['resultado_receita']}")
        print(f"  Resultado Motoristas: {meta['resultado_motoristas']}")
        print(f"  Última Atualização: {meta['updated_at']}")
else:
    print(f"✅ {len(metas_com_dados)} metas com dados reais encontradas!\n")
    
    for meta in metas_com_dados:
        cidade_nome = CIDADE_NOMES.get(meta['cidade_id'], f"Cidade {meta['cidade_id']}")
        print(f"{'='*80}")
        print(f"📍 {cidade_nome} - {meta['mes']} meses")
        print(f"{'='*80}")
        print(f"  ID: {meta['id']}")
        print(f"\n  🎯 METAS:")
        print(f"    - Corridas: {meta['meta_corridas']}")
        print(f"    - Motoristas: {meta['meta_motoristas']}")
        print(f"    - Receita: R$ {meta['meta_receita']}")
        print(f"\n  ✅ RESULTADOS:")
        print(f"    - Corridas: {meta['resultado_corridas']} ({(meta['resultado_corridas']/meta['meta_corridas']*100):.1f}%)")
        print(f"    - Motoristas: {meta['resultado_motoristas']} ({(meta['resultado_motoristas']/meta['meta_motoristas']*100):.1f}%)")
        print(f"    - Receita: R$ {meta['resultado_receita']:.2f} ({(float(meta['resultado_receita'])/float(meta['meta_receita'])*100):.1f}%)")
        print(f"    - Usuários Ativos: {meta['resultado_usuarios_ativos']}")
        print(f"    - Satisfação: {meta['resultado_satisfacao']:.2f}")
        print(f"    - Taxa Cancelamento: {meta['resultado_taxa_cancelamento']:.2f}%")
        print(f"\n  🕐 Atualizado em: {meta['updated_at']}")
        print()

conn.close()
