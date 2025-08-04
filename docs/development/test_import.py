#!/usr/bin/env python3
import requests
import os

def test_import_api():
    """Testa a API de importação"""
    
    # URL da API
    url = "http://localhost:5000/api/import/upload"
    
    # Arquivo para upload
    csv_file = "dados_exemplo.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ Arquivo {csv_file} não encontrado!")
        return
    
    print(f"📤 Testando upload do arquivo: {csv_file}")
    
    try:
        # Fazer upload do arquivo
        with open(csv_file, 'rb') as f:
            files = {'file': (csv_file, f, 'text/csv')}
            data = {'import_type': 'corridas'}
            
            response = requests.post(url, files=files, data=data)
            
        print(f"🔍 Status da resposta: {response.status_code}")
        print(f"📝 Resposta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Upload realizado com sucesso!")
                
                # Obter dados do preview
                preview_data = result['data']['preview']
                print(f"📊 Total de linhas: {preview_data['total_rows']}")
                print(f"📋 Colunas detectadas: {preview_data['columns']}")
                print(f"🔗 Mapeamento: {preview_data['detected_mapping']}")
                
                # Agora executar a importação
                import_data = {
                    'filepath': result['data']['filepath'],
                    'import_type': 'corridas',
                    'column_mapping': preview_data['detected_mapping']
                }
                
                print("\n🚀 Executando importação...")
                import_url = "http://localhost:5000/api/import/execute"
                import_response = requests.post(import_url, json=import_data)
                
                print(f"🔍 Status da importação: {import_response.status_code}")
                print(f"📝 Resultado: {import_response.text}")
                
                if import_response.status_code == 200:
                    import_result = import_response.json()
                    if import_result.get('success'):
                        print(f"✅ Importação concluída! {import_result.get('imported', 0)} registros importados")
                    else:
                        print(f"❌ Erro na importação: {import_result.get('error')}")
                else:
                    print(f"❌ Erro HTTP na importação: {import_response.status_code}")
            else:
                print(f"❌ Erro no upload: {result.get('error')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor Flask!")
        print("💡 Verifique se o servidor está rodando em http://localhost:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_import_api()
