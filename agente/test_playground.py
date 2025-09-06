"""
🧪 TESTE DO PLAYGROUND DO AGENTE
Script para testar todas as funcionalidades do playground
"""

import requests
import json
import time
import websocket
from datetime import datetime

class PlaygroundTester:
    """Classe para testar o playground"""
    
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://") + "/ws"
        
    def test_health_check(self):
        """Testa o health check"""
        print("🏥 TESTANDO HEALTH CHECK")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check OK")
                print(f"   Status: {data['status']}")
                print(f"   Agent Ready: {data['agent_ready']}")
                print(f"   Timestamp: {data['timestamp']}")
                return True
            else:
                print(f"❌ Health check falhou: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def test_web_interface(self):
        """Testa se a interface web carrega"""
        print("\n🌐 TESTANDO INTERFACE WEB")
        print("-" * 30)
        
        try:
            response = requests.get(self.base_url, timeout=10)
            
            if response.status_code == 200:
                if "Playground do Agente" in response.text:
                    print("✅ Interface web OK")
                    print(f"   Tamanho: {len(response.text)} bytes")
                    return True
                else:
                    print("❌ Interface não contém título esperado")
                    return False
            else:
                print(f"❌ Interface falhou: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao carregar interface: {e}")
            return False
    
    def test_websocket_connection(self):
        """Testa conexão WebSocket"""
        print("\n💬 TESTANDO WEBSOCKET")
        print("-" * 30)
        
        try:
            # Conectar ao WebSocket
            ws = websocket.create_connection(self.ws_url, timeout=10)
            print("✅ WebSocket conectado")
            
            # Aguardar mensagem inicial
            init_message = ws.recv()
            init_data = json.loads(init_message)
            
            if init_data.get("type") == "init":
                print("✅ Mensagem de inicialização recebida")
                print(f"   Agent Status: {init_data['data']['agent_status']}")
                
                # Fechar conexão
                ws.close()
                return True
            else:
                print(f"❌ Mensagem inesperada: {init_data}")
                ws.close()
                return False
                
        except Exception as e:
            print(f"❌ Erro no WebSocket: {e}")
            return False
    
    def test_chat_functionality(self):
        """Testa funcionalidade de chat"""
        print("\n🤖 TESTANDO CHAT COM AGENTE")
        print("-" * 30)
        
        try:
            # Conectar ao WebSocket
            ws = websocket.create_connection(self.ws_url, timeout=10)
            
            # Aguardar inicialização
            init_msg = ws.recv()
            
            # Enviar mensagem de teste
            test_message = "Olá! Como está a performance dos motoristas?"
            print(f"📤 Enviando: {test_message}")
            
            ws.send(json.dumps({
                "type": "chat",
                "message": test_message
            }))
            
            # Aguardar resposta (com timeout maior)
            start_time = time.time()
            while time.time() - start_time < 30:  # 30 segundos timeout
                try:
                    ws.settimeout(5)
                    response = ws.recv()
                    data = json.loads(response)
                    
                    if data.get("type") == "chat_response":
                        print("✅ Resposta do agente recebida")
                        print(f"   Duração: {data['data']['duration']:.2f}s")
                        print(f"   Tool calls: {data['data']['tool_calls_count']}")
                        print(f"   Resposta: {data['data']['response'][:100]}...")
                        ws.close()
                        return True
                    elif data.get("type") == "error":
                        print(f"❌ Erro do agente: {data['data']['message']}")
                        ws.close()
                        return False
                    else:
                        print(f"📝 Evento recebido: {data.get('type')}")
                        
                except websocket.WebSocketTimeoutException:
                    print("⏳ Aguardando resposta...")
                    continue
            
            print("❌ Timeout aguardando resposta do agente")
            ws.close()
            return False
            
        except Exception as e:
            print(f"❌ Erro no teste de chat: {e}")
            return False
    
    def test_stats_endpoint(self):
        """Testa endpoint de estatísticas"""
        print("\n📊 TESTANDO ESTATÍSTICAS")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/api/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Estatísticas OK")
                print(f"   Interações: {data['total_interactions']}")
                print(f"   Tool calls: {data['total_tool_calls']}")
                print(f"   Status agente: {data['agent_status']}")
                return True
            else:
                print(f"❌ Stats falhou: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro nas estatísticas: {e}")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 INICIANDO TESTES DO PLAYGROUND")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Interface Web", self.test_web_interface),
            ("WebSocket", self.test_websocket_connection),
            ("Estatísticas", self.test_stats_endpoint),
            ("Chat com Agente", self.test_chat_functionality)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ Erro inesperado no teste {test_name}: {e}")
                results[test_name] = False
        
        # Resumo
        print("\n📋 RESUMO DOS TESTES")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASSOU" if passed_test else "❌ FALHOU"
            print(f"{test_name}: {status}")
            if passed_test:
                passed += 1
        
        print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM! Playground funcionando perfeitamente.")
            return True
        else:
            print("⚠️ Alguns testes falharam. Verifique os logs acima.")
            return False

def main():
    """Função principal"""
    import sys
    
    # URL padrão ou da linha de comando
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8002"
    
    print(f"🎯 Testando playground em: {base_url}")
    
    tester = PlaygroundTester(base_url)
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 PLAYGROUND ESTÁ FUNCIONANDO!")
        print(f"🌐 Acesse: {base_url}")
        print("📊 Documentação da API: {}/docs".format(base_url))
    else:
        print("\n❌ PROBLEMAS DETECTADOS NO PLAYGROUND")
        print("💡 Verifique se o playground está rodando: python playground.py")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
