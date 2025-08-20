#!/usr/bin/env python3
"""
🧪 TESTE DO SISTEMA DE PROGRESSO AUTOMÁTICO POR PADRÃO

Testa se as fases estão calculando progresso automaticamente quando não é manual
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def testar_progresso_automatico():
    """Testa se o progresso automático está sendo calculado por padrão"""
    
    print("🧪 TESTANDO PROGRESSO AUTOMÁTICO POR PADRÃO")
    print("=" * 60)
    
    try:
        # 1️⃣ Buscar fases atuais
        print("\n1️⃣ Buscando fases de planejamento...")
        response = requests.get(f"{API_BASE}/metas-estrategicas/fases-planejamento")
        
        if response.status_code == 200:
            data = response.json()
            
            # A resposta é diretamente uma lista (não tem 'fases' como chave)
            if isinstance(data, list):
                fases = data
            else:
                fases = data.get('fases', [])
            
            print(f"✅ {len(fases)} fases encontradas")
            
            for fase in fases:
                print(f"\n📋 FASE: {fase.get('nome', 'N/A')}")
                print(f"   ID: {fase.get('id')}")
                print(f"   Progresso: {fase.get('progresso_percentual', 0):.1f}%")
                print(f"   Manual: {fase.get('progresso_manual', False)}")
                print(f"   Método: {fase.get('metodo_calculo', 'N/A')}")
                print(f"   Automático: {fase.get('progresso_automatico', 'N/A')}")
                
                if 'metodo_usado' in fase:
                    print(f"   Método Usado: {fase['metodo_usado']}")
                
        else:
            print(f"❌ Erro ao buscar fases: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro na execução: {e}")

def testar_alternar_modo():
    """Testa alternar entre manual e automático"""
    
    print("\n\n🔄 TESTANDO ALTERNÂNCIA MANUAL/AUTOMÁTICO")
    print("=" * 60)
    
    try:
        # Buscar primeira fase para testar
        response = requests.get(f"{API_BASE}/metas-estrategicas/fases-planejamento")
        if response.status_code == 200:
            data = response.json()
            
            # A resposta é diretamente uma lista
            if isinstance(data, list):
                fases = data
            else:
                fases = data.get('fases', [])
                
            if fases:
                fase_id = fases[0]['id']
                print(f"\n🎯 Testando com fase ID: {fase_id}")
                
                # Testar alternar para manual
                print("\n2️⃣ Alternando para modo MANUAL...")
                response = requests.post(
                    f"{API_BASE}/metas-estrategicas/fases-estrategicas/{fase_id}/alternar-progresso",
                    json={
                        "progresso_manual": True,
                        "progresso_percentual": 75.5
                    }
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    print("✅ Alternado para manual:")
                    print(f"   Progresso: {resultado.get('progresso_percentual')}%")
                    print(f"   Manual: {resultado.get('progresso_manual')}")
                else:
                    print(f"❌ Erro ao alternar para manual: {response.status_code}")
                    print(response.text)
                
                # Testar alternar para automático
                print("\n3️⃣ Alternando para modo AUTOMÁTICO...")
                response = requests.post(
                    f"{API_BASE}/metas-estrategicas/fases-estrategicas/{fase_id}/alternar-progresso",
                    json={
                        "progresso_manual": False
                    }
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    print("✅ Alternado para automático:")
                    print(f"   Progresso: {resultado.get('progresso_percentual')}%")
                    print(f"   Manual: {resultado.get('progresso_manual')}")
                    print(f"   Método: {resultado.get('metodo_calculo')}")
                else:
                    print(f"❌ Erro ao alternar para automático: {response.status_code}")
                    print(response.text)
                    
    except Exception as e:
        print(f"❌ Erro na alternância: {e}")

if __name__ == "__main__":
    testar_progresso_automatico()
    testar_alternar_modo()
    print("\n\n🏁 TESTE CONCLUÍDO!")
