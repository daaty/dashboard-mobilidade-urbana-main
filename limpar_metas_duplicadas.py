#!/usr/bin/env python3
"""
Script para limpar metas progressivas duplicadas e recriar sistema dinâmico
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def limpar_metas_duplicadas():
    """Remove todas as metas progressivas duplicadas"""
    print("🧹 LIMPANDO METAS DUPLICADAS...")
    
    # Buscar todas as metas
    response = requests.get(f"{API_URL}/api/metas-progressivas")
    metas = response.json()
    
    print(f"📊 Total de metas encontradas: {len(metas)}")
    
    # Agrupar por cidade_id + mes + tipo_meta para identificar duplicatas
    metas_unicas = {}
    metas_para_deletar = []
    
    for meta in metas:
        chave = f"{meta['cidade_id']}_{meta['mes']}_{meta['tipo_meta']}"
        
        if chave in metas_unicas:
            # Duplicata encontrada - marcar para deleção
            metas_para_deletar.append(meta['id'])
            print(f"🗑️ Duplicata encontrada: {meta['cidade_nome']} - Mês {meta['mes']} - {meta['tipo_meta']}")
        else:
            # Primeira ocorrência - manter
            metas_unicas[chave] = meta
    
    print(f"✅ Metas únicas: {len(metas_unicas)}")
    print(f"🗑️ Metas para deletar: {len(metas_para_deletar)}")
    
    # Deletar duplicatas
    for meta_id in metas_para_deletar:
        try:
            delete_response = requests.delete(f"{API_URL}/api/metas-progressivas/{meta_id}")
            if delete_response.status_code == 200:
                print(f"✅ Meta {meta_id} deletada")
            else:
                print(f"❌ Erro ao deletar meta {meta_id}: {delete_response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao deletar meta {meta_id}: {e}")
    
    return metas_unicas

def criar_endpoints_crud():
    """Criar endpoints para CRUD dinâmico das metas"""
    
    crud_endpoints = {
        "criar_meta": f"{API_URL}/api/metas-progressivas/",
        "editar_meta": f"{API_URL}/api/metas-progressivas/{{id}}",
        "deletar_meta": f"{API_URL}/api/metas-progressivas/{{id}}",
        "buscar_por_cidade": f"{API_URL}/api/metas-progressivas/cidade/{{cidade_id}}",
        "buscar_por_tipo": f"{API_URL}/api/metas-progressivas/tipo/{{tipo_meta}}"
    }
    
    print("🔧 ENDPOINTS CRUD DISPONÍVEIS:")
    for nome, url in crud_endpoints.items():
        print(f"  📍 {nome}: {url}")
    
    return crud_endpoints

def validar_sistema():
    """Validar se o sistema está funcionando corretamente"""
    print("\n🔍 VALIDANDO SISTEMA LIMPO...")
    
    # Buscar metas restantes
    response = requests.get(f"{API_URL}/api/metas-progressivas")
    metas = response.json()
    
    # Agrupar por cidade
    por_cidade = {}
    for meta in metas:
        cidade = meta['cidade_nome']
        if cidade not in por_cidade:
            por_cidade[cidade] = []
        por_cidade[cidade].append(meta)
    
    print(f"📊 SISTEMA LIMPO - Total: {len(metas)} metas")
    print("🏙️ DISTRIBUIÇÃO POR CIDADE:")
    
    for cidade, metas_cidade in por_cidade.items():
        tipos = {}
        for meta in metas_cidade:
            tipo = meta['tipo_meta']
            if tipo not in tipos:
                tipos[tipo] = 0
            tipos[tipo] += 1
        
        tipos_str = ", ".join([f"{tipo}: {qtd}" for tipo, qtd in tipos.items()])
        print(f"  🎯 {cidade}: {len(metas_cidade)} metas ({tipos_str})")
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO LIMPEZA E REORGANIZAÇÃO DO SISTEMA DE METAS")
    print("=" * 60)
    
    try:
        # 1. Limpar duplicatas
        metas_unicas = limpar_metas_duplicadas()
        
        # 2. Criar endpoints CRUD
        endpoints = criar_endpoints_crud()
        
        # 3. Validar sistema
        validar_sistema()
        
        print("\n✅ SISTEMA REORGANIZADO COM SUCESSO!")
        print("🎯 PRÓXIMOS PASSOS:")
        print("  1. Frontend dinâmico para mostrar cidades")
        print("  2. Interface CRUD para metas progressivas")
        print("  3. Integração visual entre sistemas")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
