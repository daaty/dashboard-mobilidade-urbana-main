"""
🧪 TESTE RÁPIDO DOS ENDPOINTS DE CÁLCULO DE PROGRESSO

Execute este arquivo para testar se os endpoints estão funcionando corretamente
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def testar_endpoints():
    print("🧪 Testando endpoints de cálculo de progresso...\n")
    
    # 1. Testar endpoint de configuração
    print("1️⃣ Testando configuração...")
    try:
        response = requests.get(f"{BASE_URL}/api/metas-estrategicas/configuracao-progresso")
        if response.status_code == 200:
            print("✅ Configuração OK")
            config = response.json()
            print(f"   Métodos disponíveis: {list(config['metodos_disponiveis'].keys())}")
        else:
            print(f"❌ Erro na configuração: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print()
    
    # 2. Listar fases disponíveis
    print("2️⃣ Listando fases estratégicas...")
    try:
        response = requests.get(f"{BASE_URL}/api/metas-estrategicas/fases-planejamento")
        if response.status_code == 200:
            fases_response = response.json()
            print(f"✅ Resposta recebida")
            print(f"   Tipo: {type(fases_response)}")
            print(f"   Conteúdo: {fases_response}")
            
            # Verificar se é uma lista ou objeto com chave 'fases'
            if isinstance(fases_response, list):
                fases = fases_response
            elif isinstance(fases_response, dict) and 'fases' in fases_response:
                fases = fases_response['fases']
            else:
                print("   ⚠️ Formato de resposta não reconhecido")
                return
            
            print(f"   Encontradas {len(fases)} fases")
            
            if fases:
                # Mostrar detalhes das fases
                for i, fase in enumerate(fases):
                    if isinstance(fase, dict):
                        print(f"   Fase {i+1}: {fase.get('nome', 'Sem nome')} (ID: {fase.get('id', 'Sem ID')})")
                    else:
                        print(f"   Fase {i+1}: {fase} (formato inesperado)")
                
                # 3. Testar cálculo em uma fase válida
                fase_teste = None
                for fase in fases:
                    if isinstance(fase, dict) and fase.get('id') and fase.get('id') > 0:
                        fase_teste = fase
                        break
                
                if fase_teste:
                    fase_id = fase_teste.get('id')
                    print(f"\n   Testando cálculo na fase: {fase_teste.get('nome', 'Sem nome')} (ID: {fase_id})")
                    
                    print("\n3️⃣ Testando cálculo de progresso...")
                    for metodo in ['temporal', 'orcamentario', 'metas', 'hibrido']:
                        try:
                            calc_response = requests.post(
                                f"{BASE_URL}/api/metas-estrategicas/fases-estrategicas/{fase_id}/calcular-progresso",
                                params={'metodo': metodo}
                            )
                            
                            if calc_response.status_code == 200:
                                resultado = calc_response.json()
                                if resultado.get('success'):
                                    progresso = resultado.get('progresso_novo', 0)
                                    print(f"   ✅ {metodo.capitalize()}: {progresso:.1f}%")
                                else:
                                    print(f"   ⚠️ {metodo.capitalize()}: {resultado.get('error', 'Erro desconhecido')}")
                            else:
                                print(f"   ❌ {metodo.capitalize()}: HTTP {calc_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ {metodo.capitalize()}: Erro - {e}")
                else:
                    print("   ⚠️ Nenhuma fase com ID válido encontrada para testar")
            else:
                print("   ⚠️ Nenhuma fase encontrada para testar")
        else:
            print(f"❌ Erro ao listar fases: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n🏁 Teste concluído!")

if __name__ == "__main__":
    testar_endpoints()
