# SOLUÇÃO: N8N EXPRESSION MODE

## ❌ PROBLEMA IDENTIFICADO:
O N8N está enviando `"{{ $json.kind }}"` literalmente em vez de processar as expressions.

## ✅ SOLUÇÃO: USAR EXPRESSION MODE

### 🔧 CONFIGURAÇÃO CORRETA NO N8N:

1. **HTTP Request Node**
2. **Method:** POST
3. **URL:** https://agno.rotadoscelulares.com/financial/register
4. **Send Body:** Yes
5. **Body Content Type:** JSON
6. **No campo JSON Body:** Clique no ícone **Expression (fx)**
7. **Cole este código no Expression:**

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

### 🔧 SE OS DADOS VÊM COMO ARRAY [0]:

```javascript
{
  "kind": $json[0].kind,
  "id": $json[0].id,
  "name": $json[0].name,
  "mimeType": $json[0].mimeType,
  "webContentLink": $json[0].webContentLink,
  "webViewLink": $json[0].webViewLink,
  "content": {
    "parts": [
      {
        "text": $json[0].content.parts[0].text
      }
    ],
    "role": $json[0].content.role
  }
}
```

## ⚠️ DIFERENÇA IMPORTANTE:

### ❌ ERRADO (modo texto):
```json
"kind": "{{ $json.kind }}"
```

### ✅ CORRETO (modo expression):
```javascript
"kind": $json.kind
```

## 🎯 PASSO A PASSO:

1. **Abra** o HTTP Request node
2. **Configure** Method: POST, URL: https://agno.rotadoscelulares.com/financial/register
3. **Ative** Send Body → JSON
4. **No campo JSON Body:** Clique no ícone **fx** (Expression)
5. **Cole** uma das expressions acima
6. **Salve** e teste

## 🧪 TESTE:

Agora o N8N vai processar as expressions corretamente e enviar JSON válido para o endpoint.
