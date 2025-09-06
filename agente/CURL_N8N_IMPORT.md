# CURL PARA IMPORTAR NO N8N HTTP REQUEST

## 📋 CURL COMANDO COMPLETO:

```bash
curl -X POST \
  'https://agno.rotadoscelulares.com/financial/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "kind": "drive#file",
    "id": "1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8",
    "name": "comprovante_outro_20250905_203546.jpg",
    "mimeType": "text/html",
    "webContentLink": "https://drive.google.com/uc?id=1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8&export=download",
    "webViewLink": "https://drive.google.com/file/d/1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8/view?usp=drivesdk",
    "content": {
      "parts": [
        {
          "text": "```json\n{\n  \"dados_extraidos\": {\n    \"data_despesa\": \"2025-09-05\",\n    \"valor_total\": 150.75,\n    \"descricao_item\": \"Combustível para veículo da empresa\",\n    \"tipo_documento\": \"Comprovante\",\n    \"fornecedor\": \"Posto Shell\"\n  },\n  \"descricao_imagem\": \"Comprovante de pagamento de combustível no Posto Shell. Data: 05/09/2025. Valor: R$ 150,75. Produto: Gasolina comum. Placa do veículo: ABC-1234.\"\n}\n```"
        }
      ],
      "role": "model"
    }
  }'
```

## 🔧 COMO IMPORTAR NO N8N:

### Método 1: Import cURL
1. Abra o N8N
2. Clique em "Add Node" → "HTTP Request"
3. No HTTP Request node, clique no menu "..." → "Import cURL"
4. Cole o comando CURL acima
5. O N8N vai configurar automaticamente tudo!

### Método 2: Configuração Manual
Se a importação não funcionar, configure manualmente:

**Method:** POST
**URL:** https://agno.rotadoscelulares.com/financial/register
**Send Body:** Yes
**Body Content Type:** JSON
**JSON Body:**
```json
{
  "kind": "{{ $json.kind }}",
  "id": "{{ $json.id }}",
  "name": "{{ $json.name }}",
  "mimeType": "{{ $json.mimeType }}",
  "webContentLink": "{{ $json.webContentLink }}",
  "webViewLink": "{{ $json.webViewLink }}",
  "content": {
    "parts": [
      {
        "text": "{{ $json.content.parts[0].text }}"
      }
    ],
    "role": "{{ $json.content.role }}"
  }
}
```

## 🧪 CURL SIMPLIFICADO PARA TESTE:

```bash
curl -X POST \
  'https://agno.rotadoscelulares.com/financial/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "teste.jpg",
    "webContentLink": "https://example.com/test",
    "content": {
      "parts": [
        {
          "text": "```json\n{\"dados_extraidos\":{\"data_despesa\":\"2025-09-05\",\"valor_total\":100.50,\"descricao_item\":\"Teste\",\"tipo_documento\":\"Comprovante\",\"fornecedor\":\"Teste\"},\"descricao_imagem\":\"Teste\"}\n```"
        }
      ]
    }
  }'
```

## ✅ RESPOSTA ESPERADA:

```json
{
  "success": true,
  "message": "Gasto registrado com sucesso!",
  "gasto_id": 527126,
  "data": {
    "data_despesa": "2025-09-05",
    "valor_total": 150.75,
    "descricao_item": "Combustível para veículo da empresa",
    "tipo_documento": "Comprovante",
    "fornecedor": "Posto Shell",
    "link_arquivo": "https://drive.google.com/uc?id=1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8&export=download",
    "nome_arquivo": "comprovante_outro_20250905_203546.jpg"
  }
}
```

## 🎯 PASSOS FINAIS:

1. **Teste o CURL** no terminal primeiro para validar
2. **Importe no N8N** usando o método 1
3. **Substitua os valores fixos** pelas variáveis do seu workflow
4. **Execute** e verifique se o gasto foi registrado!

## 📝 NOTA IMPORTANTE:

Certifique-se de que:
- ✅ O servidor está rodando (python mobility_playground.py)
- ✅ O tunnel está ativo para agno.rotadoscelulares.com
- ✅ Os dados vêm no formato array ([0]) como mostrado nos seus dados reais
