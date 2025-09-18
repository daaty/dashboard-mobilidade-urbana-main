import requests
import json

def test_passenger_edit():
    base_url = "http://localhost:8000/api/passengers"
    
    print("=== TESTANDO EDIÇÃO DE PASSAGEIROS ===\n")
    
    # Primeiro buscar um passageiro específico para testar
    print("1. 🔍 BUSCANDO PASSAGEIRO HALEF PARA TESTE")
    response = requests.get(f"{base_url}/list?search=halef&limit=10")
    
    if response.status_code != 200:
        print(f"❌ Erro ao buscar passageiros: {response.status_code}")
        return
    
    passengers = response.json()
    if not passengers:
        print("❌ Nenhum passageiro Halef encontrado")
        return
    
    # Usar o primeiro Halef encontrado
    passenger = passengers[0]
    passenger_id = passenger['passenger_id']
    
    print(f"✅ Passageiro encontrado: {passenger['user_name']} (ID: {passenger_id})")
    print(f"   📧 Email atual: {passenger['user_email']}")
    print(f"   📱 Telefone atual: {passenger['user_phone']}")
    print(f"   🏙️ Cidade atual: {passenger['city']}")
    print(f"   📊 Status atual: {passenger['status']}")
    
    print("\n" + "-"*50 + "\n")
    
    # Teste de edição
    print("2. ✏️  TESTANDO EDIÇÃO DO PASSAGEIRO")
    
    update_data = {
        "user_name": passenger['user_name'] + " (EDITADO TESTE)",
        "user_email": "teste_editado@exemplo.com", 
        "user_phone": "+5566999999999",
        "city": "CIDADE TESTE",
        "blocked": "No"  # Manter ativo
    }
    
    print("📝 Dados para atualização:")
    for key, value in update_data.items():
        print(f"   {key}: {value}")
    
    # Fazer a requisição PUT
    response = requests.put(
        f"{base_url}/{passenger_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ EDIÇÃO BEM-SUCEDIDA: {result['message']}")
    else:
        print(f"❌ ERRO NA EDIÇÃO: {response.status_code}")
        print(f"   Detalhes: {response.text}")
        return
    
    print("\n" + "-"*50 + "\n")
    
    # Verificar se as mudanças foram aplicadas
    print("3. 🔍 VERIFICANDO SE AS MUDANÇAS FORAM APLICADAS")
    
    response = requests.get(f"{base_url}/list?search=EDITADO&limit=10")
    if response.status_code == 200:
        updated_passengers = response.json()
        if updated_passengers:
            updated_passenger = updated_passengers[0]
            print("✅ PASSAGEIRO ATUALIZADO ENCONTRADO:")
            print(f"   👤 Nome: {updated_passenger['user_name']}")
            print(f"   📧 Email: {updated_passenger['user_email']}")
            print(f"   📱 Telefone: {updated_passenger['user_phone']}")
            print(f"   🏙️ Cidade: {updated_passenger['city']}")
            print(f"   📊 Status: {updated_passenger['status']}")
            
            # Verificar se todos os campos foram atualizados
            success = True
            if "EDITADO TESTE" not in updated_passenger['user_name']:
                print("❌ Nome não foi atualizado")
                success = False
            if updated_passenger['user_email'] != "teste_editado@exemplo.com":
                print("❌ Email não foi atualizado")
                success = False
            if updated_passenger['user_phone'] != "+5566999999999":
                print("❌ Telefone não foi atualizado") 
                success = False
            if updated_passenger['city'] != "CIDADE TESTE":
                print("❌ Cidade não foi atualizada")
                success = False
            if updated_passenger['status'] != "Ativo":
                print("❌ Status não foi atualizado")
                success = False
                
            if success:
                print("\n🎉 TODOS OS CAMPOS FORAM ATUALIZADOS COM SUCESSO!")
            else:
                print("\n⚠️  ALGUMAS ATUALIZAÇÕES FALHARAM")
        else:
            print("❌ Passageiro atualizado não encontrado na busca")
    else:
        print(f"❌ Erro ao verificar atualização: {response.status_code}")

if __name__ == "__main__":
    test_passenger_edit()