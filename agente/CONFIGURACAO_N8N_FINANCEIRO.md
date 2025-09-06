# CONFIGURAÇÃO CORRETA DO N8N PARA O AGENTE FINANCEIRO

## 📋 DADOS RECEBIDOS DA ANÁLISE DA IMAGEM:
Os dados vêm em um array, onde o primeiro elemento [0] contém todas as informações necessárias.

## 🎯 REQUEST CORRETO NO N8N:

### HTTP Request Node Configuration:
```json
{
  "method": "POST",
  "url": "https://agno.rotadoscelulares.com/financial/register",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": {
    "kind": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].kind }}",
    "id": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].id }}",
    "name": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].name }}",
    "mimeType": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].mimeType }}",
    "webContentLink": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].webContentLink }}",
    "webViewLink": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].webViewLink }}",
    "content": {
      "parts": [
        {
          "text": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].content.parts[0].text }}"
        }
      ],
      "role": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].content.role }}"
    }
  }
}
```

### 🔧 SUBSTITUA "NOME_DO_NO_ANTERIOR" pelo nome real do nó que fornece os dados da análise da imagem.

## 📝 EXEMPLO COM OS DADOS REAIS:

Baseado nos seus dados, o JSON ficaria assim:

```json
{
  "kind": "drive#file",
  "id": "1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8",
  "name": "comprovante_outro_20250905_203546.jpg",
  "mimeType": "text/html",
  "webContentLink": "https://drive.google.com/uc?id=1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8&export=download",
  "webViewLink": "https://drive.google.com/file/d/1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8/view?usp=drivesdk",
  "content": {
    "parts": [
      {
        "text": "```json\n{\n  \"dados_extraidos\": {\n    \"data_despesa\": null,\n    \"valor_total\": null,\n    \"descricao_item\": \"Página de erro 404\",\n    \"tipo_documento\": \"Outro\",\n    \"fornecedor\": null\n  },\n  \"descricao_imagem\": \"A imagem exibe uma página de erro 404...\"\n}\n```\n"
      }
    ],
    "role": "model"
  }
}
```

## ⚡ VERSÃO SIMPLIFICADA (RECOMENDADA):

Se quiser usar uma versão mais simples, pode enviar apenas os campos essenciais:

```json
{
  "name": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].name }}",
  "webContentLink": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].webContentLink }}",
  "content": {
    "parts": [
      {
        "text": "{{ $('NOME_DO_NO_ANTERIOR').item.json[0].content.parts[0].text }}"
      }
    ]
  }
}
```

## 🎯 PONTOS IMPORTANTES:

1. **Array**: Os dados vêm em um array, então use `[0]` para acessar o primeiro elemento
2. **content.parts[0].text**: Aqui está a análise JSON da imagem
3. **webContentLink**: Link para download do arquivo no Google Drive
4. **name**: Nome do arquivo (importante para rastreamento)

## 🔧 CONFIGURAÇÃO NO N8N:

1. Método: `POST`
2. URL: `https://agno.rotadoscelulares.com/financial/register`
3. Content-Type: `application/json`
4. Body: Use o JSON acima com os mapeamentos corretos

## ✅ TESTE:

Após configurar, teste com:
- GET `https://agno.rotadoscelulares.com/financial/health` (deve retornar status: healthy)
- POST com os dados reais

O agente vai automaticamente:
1. Extrair o JSON do `content.parts[0].text`
2. Validar os dados extraídos
3. Inserir na tabela `gastos_empresa`
4. Retornar confirmação com ID do gasto
