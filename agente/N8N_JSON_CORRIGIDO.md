# CONFIGURAÇÃO CORRIGIDA DO N8N

## ❌ PROBLEMA: "JSON parameter needs to be valid JSON"

O erro acontece porque as aspas duplas dentro do JSON estão causando conflito.

## ✅ SOLUÇÃO 1: JSON SIMPLES (RECOMENDADO)

No HTTP Request node, use esta configuração:

### Method: POST
### URL: https://agno.rotadoscelulares.com/financial/register
### Body Type: JSON
### JSON Body:

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

## ✅ SOLUÇÃO 2: USANDO EXPRESSION (ALTERNATIVA)

Se a primeira não funcionar, tente com Expression:

### No campo JSON Body, clique no ícone de Expression (fx) e cole:

```javascript
{
  "kind": $json.kind,
  "id": $json.id,
  "name": $json.name,
  "mimeType": $json.mimeType,
  "webContentLink": $json.webContentLink,
  "webViewLink": $json.webViewLink,
  "content": {
    "parts": [
      {
        "text": $json.content.parts[0].text
      }
    ],
    "role": $json.content.role
  }
}
```

## ✅ SOLUÇÃO 3: VERSÃO MÍNIMA (MAIS SIMPLES)

Se ainda der erro, use apenas os campos essenciais:

```json
{
  "name": "{{ $json.name }}",
  "webContentLink": "{{ $json.webContentLink }}",
  "content": {
    "parts": [
      {
        "text": "{{ $json.content.parts[0].text }}"
      }
    ]
  }
}
```

## 🔧 CONFIGURAÇÃO PASSO A PASSO:

1. **HTTP Request Node**
2. **Method**: POST
3. **URL**: https://agno.rotadoscelulares.com/financial/register
4. **Send Body**: true
5. **Body Content Type**: JSON
6. **JSON**: Cole uma das soluções acima

## 🧪 TESTE ANTES DE CONECTAR:

Teste o endpoint primeiro com dados fixos para verificar se está funcionando:

```json
{
  "kind": "drive#file",
  "id": "test123",
  "name": "teste.jpg",
  "mimeType": "text/html",
  "webContentLink": "https://example.com/test",
  "webViewLink": "https://example.com/view",
  "content": {
    "parts": [
      {
        "text": "```json\n{\"dados_extraidos\":{\"data_despesa\":\"2025-09-05\",\"valor_total\":100.50,\"descricao_item\":\"Teste\",\"tipo_documento\":\"Comprovante\",\"fornecedor\":\"Teste\"},\"descricao_imagem\":\"Teste\"}\n```"
      }
    ],
    "role": "model"
  }
}
```
