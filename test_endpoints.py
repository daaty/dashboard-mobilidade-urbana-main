"""
Script para testar os novos endpoints de driver_personal_details
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_endpoints():
    async with httpx.AsyncClient() as client:
        print("=== TESTANDO ENDPOINTS DRIVER PERSONAL DETAILS ===\n")
        
        # 1. Testar /api/drivers/cities
        print("1. Testando /api/drivers/cities")
        try:
            response = await client.get(f"{BASE_URL}/api/drivers/cities")
            if response.status_code == 200:
                cities = response.json()
                print(f"✅ Sucesso: {len(cities)} cidades encontradas")
                print(f"   Cidades: {cities}")
            else:
                print(f"❌ Erro: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
        
        print()
        
        # 2. Testar /api/drivers/summary
        print("2. Testando /api/drivers/summary")
        try:
            response = await client.get(f"{BASE_URL}/api/drivers/summary")
            if response.status_code == 200:
                summary = response.json()
                print(f"✅ Sucesso: Resumo obtido")
                print(f"   Total drivers: {summary['total_drivers']}")
                print(f"   Drivers ativos: {summary['active_drivers']}")
                print(f"   Total corridas: {summary['total_rides']}")
                print(f"   Ganhos totais: R$ {summary['total_earnings']:.2f}")
            else:
                print(f"❌ Erro: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
        
        print()
        
        # 3. Testar /api/drivers/personal-details (com paginação)
        print("3. Testando /api/drivers/personal-details")
        try:
            response = await client.get(f"{BASE_URL}/api/drivers/personal-details?page=1&limit=5")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sucesso: {len(data['drivers'])} drivers na página 1")
                print(f"   Total: {data['total_count']} drivers")
                if data['drivers']:
                    first_driver = data['drivers'][0]
                    print(f"   Primeiro driver: {first_driver['name']} (ID: {first_driver['driver_id']})")
            else:
                print(f"❌ Erro: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
        
        print()
        
        # 4. Testar /api/drivers/personal-details/{driver_id} para um driver específico
        print("4. Testando detalhes de um driver específico")
        try:
            # Primeiro pegar um driver ID
            response = await client.get(f"{BASE_URL}/api/drivers/personal-details?limit=1")
            if response.status_code == 200:
                data = response.json()
                if data['drivers']:
                    driver_id = data['drivers'][0]['driver_id']
                    
                    # Agora buscar os detalhes
                    response = await client.get(f"{BASE_URL}/api/drivers/personal-details/{driver_id}")
                    if response.status_code == 200:
                        driver_details = response.json()
                        print(f"✅ Sucesso: Detalhes do driver {driver_id}")
                        print(f"   Cidade: {driver_details['city']}")
                        print(f"   Nome: {driver_details['personal_data'].get('name', 'N/A')}")
                    else:
                        print(f"❌ Erro: Status {response.status_code}")
                else:
                    print("❌ Nenhum driver encontrado para teste")
            else:
                print(f"❌ Erro ao buscar drivers: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
        
        print()
        
        # 5. Testar /api/drivers/analytics/{driver_id}
        print("5. Testando analytics de um driver específico")
        try:
            # Usar o mesmo driver ID do teste anterior
            response = await client.get(f"{BASE_URL}/api/drivers/personal-details?limit=1")
            if response.status_code == 200:
                data = response.json()
                if data['drivers']:
                    driver_id = data['drivers'][0]['driver_id']
                    
                    # Buscar analytics
                    response = await client.get(f"{BASE_URL}/api/drivers/analytics/{driver_id}")
                    if response.status_code == 200:
                        analytics = response.json()
                        print(f"✅ Sucesso: Analytics do driver {driver_id}")
                        print(f"   Total corridas: {analytics['total_rides']}")
                        print(f"   Taxa de conclusão: {analytics['completion_rate']:.2f}%")
                        print(f"   Ganhos totais: R$ {analytics['total_earnings']:.2f}")
                        print(f"   Rating médio: {analytics['average_rating']}")
                    else:
                        print(f"❌ Erro: Status {response.status_code}")
                else:
                    print("❌ Nenhum driver encontrado para teste")
            else:
                print(f"❌ Erro ao buscar drivers: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    print("Iniciando testes dos endpoints...")
    print("Certifique-se de que o servidor FastAPI está rodando em http://localhost:8000\n")
    
    try:
        asyncio.run(test_endpoints())
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\nErro geral: {e}")
    
    print("\n=== TESTES CONCLUÍDOS ===")
