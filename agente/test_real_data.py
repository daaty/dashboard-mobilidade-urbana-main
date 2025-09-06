#!/usr/bin/env python3
"""
Teste com dados REAIS da análise da imagem
"""
import requests
import json

# Dados REAIS que o N8N vai enviar
real_data = {
    "kind": "drive#file",
    "id": "1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8",
    "name": "comprovante_outro_20250905_203546.jpg",
    "mimeType": "text/html",
    "webContentLink": "https://drive.google.com/uc?id=1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8&export=download",
    "webViewLink": "https://drive.google.com/file/d/1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8/view?usp=drivesdk",
    "content": {
        "parts": [
            {
                "text": """```json
{
  "dados_extraidos": {
    "data_despesa": null,
    "valor_total": null,
    "descricao_item": "Página de erro 404",
    "tipo_documento": "Outro",
    "fornecedor": null
  },
  "descricao_imagem": "A imagem exibe uma página de erro 404 estilizada, indicando que a página solicitada não foi encontrada. O fundo da página é cinza claro (#EFEFEF). Uma caixa branca com bordas arredondadas domina o centro da imagem. Esta caixa contém o título principal em vermelho escuro (#730E15): 'The page you were looking for doesn't exist.'. Abaixo do título, há um parágrafo em preto que diz: 'You may have mistyped the address or the page may have moved.'. Na parte inferior da caixa, há outro parágrafo em cinza que informa: 'If you are the application owner check the logs for more information.'. A fonte utilizada é Arial, sans-serif. A composição é simples e direta, com foco na mensagem de erro. O tom geral é informativo e um pouco frustrante, típico de uma página de erro."
}
```"""
            }
        ],
        "role": "model"
    }
}

def test_with_real_data():
    """Testa com dados reais da análise"""
    
    endpoint = "https://agno.rotadoscelulares.com/financial/register"
    
    print("🧪 TESTE COM DADOS REAIS DA ANÁLISE")
    print("=" * 50)
    print(f"📍 Endpoint: {endpoint}")
    print(f"📋 Arquivo: {real_data['name']}")
    print(f"🔗 Link: {real_data['webContentLink']}")
    print()
    
    # Mostrar o JSON extraído
    import re
    text = real_data['content']['parts'][0]['text']
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        extracted_json = json.loads(json_match.group(1))
        print("📄 JSON EXTRAÍDO:")
        print(json.dumps(extracted_json, indent=2, ensure_ascii=False))
        print()
    
    try:
        response = requests.post(
            endpoint,
            json=real_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RESPOSTA:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                print(f"\n🎯 Sucesso: {result.get('message')}")
                if result.get('gasto_id'):
                    print(f"💾 ID do gasto: {result.get('gasto_id')}")
            else:
                print(f"\n❌ Erro: {result.get('error')}")
                
        else:
            print("❌ ERRO!")
            print(f"📨 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_with_real_data()
    
    print("\n" + "=" * 50)
    print("📝 CONFIGURAÇÃO N8N (JSON BODY):")
    print(json.dumps({
        "kind": "{{ $('NOME_DO_NO').item.json[0].kind }}",
        "id": "{{ $('NOME_DO_NO').item.json[0].id }}",
        "name": "{{ $('NOME_DO_NO').item.json[0].name }}",
        "mimeType": "{{ $('NOME_DO_NO').item.json[0].mimeType }}",
        "webContentLink": "{{ $('NOME_DO_NO').item.json[0].webContentLink }}",
        "webViewLink": "{{ $('NOME_DO_NO').item.json[0].webViewLink }}",
        "content": {
            "parts": [
                {
                    "text": "{{ $('NOME_DO_NO').item.json[0].content.parts[0].text }}"
                }
            ],
            "role": "{{ $('NOME_DO_NO').item.json[0].content.role }}"
        }
    }, indent=2))
    print("\n🔧 Substitua 'NOME_DO_NO' pelo nome real do nó anterior!")
