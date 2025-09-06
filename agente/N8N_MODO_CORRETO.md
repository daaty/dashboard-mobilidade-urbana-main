# CONFIGURAÇÃO CORRETA PARA N8N

## ✅ MODO JSON (RECOMENDADO)

**Body Content Type:** JSON
**JSON Body:**

```json
{
  "kind": "={{ $json.kind }}",
  "id": "={{ $json.id }}",
  "name": "={{ $json.name }}",
  "mimeType": "={{ $json.mimeType }}",
  "webContentLink": "={{ $json.webContentLink }}",
  "webViewLink": "={{ $json.webViewLink }}",
  "content": {
    "parts": [
      {
        "text": "={{ $json.content.parts[0].text }}"
      }
    ],
    "role": "={{ $json.content.role }}"
  }
}
```

## ✅ MODO EXPRESSION (ALTERNATIVO)

**Body Content Type:** Expression
**Expression:**

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

## 🔧 DIFERENÇAS:

- **JSON Mode**: Use `"={{ variavel }}"` (com aspas duplas)
- **Expression Mode**: Use `variavel` (sem aspas, sem chaves duplas)

## 🎯 TESTE PRIMEIRO:

Use o **MODO JSON** que é mais simples e compatível!
