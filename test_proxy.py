#!/usr/bin/env python3
import requests

def test_frontend_backend_communication():
    """Testa se o frontend consegue se comunicar com o backend através do proxy"""
    
    # Testar acesso direto ao backend
    print("🔍 Testando acesso direto ao backend...")
    try:
        response = requests.get("http://localhost:5000/api/dashboard/overview")
        if response.status_code == 200:
            print("✅ Backend funcionando: ", response.json()["data"]["metricas_principais"]["total_corridas"])
        else:
            print("❌ Backend com erro:", response.status_code)
    except Exception as e:
        print("❌ Backend não acessível:", e)
    
    # Testar acesso através do proxy do Vite (frontend)
    print("\n🔍 Testando acesso através do proxy do Vite...")
    try:
        # O frontend está em localhost:3000, então o proxy deveria redirecionr /api/* para o backend
        response = requests.get("http://localhost:3000/api/dashboard/overview")
        if response.status_code == 200:
            print("✅ Proxy funcionando: ", response.json()["data"]["metricas_principais"]["total_corridas"])
        else:
            print("❌ Proxy com erro:", response.status_code, response.text)
    except Exception as e:
        print("❌ Proxy não funcionando:", e)

if __name__ == "__main__":
    test_frontend_backend_communication()
