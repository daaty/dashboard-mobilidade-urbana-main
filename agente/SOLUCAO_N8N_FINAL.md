**INSTRUÇÕES PARA CONFIGURAR NO N8N:**

1. **Não use JSON mode!** Use "Form-URL-Encoded" ou "Raw/Custom"

2. **Se for usar Raw/Custom:**
   - Content-Type: application/json
   - Body: 
```
{
  "kind": "{{ $json.kind }}",
  "id": "{{ $json.id }}",
  "name": "{{ $json.name }}",
  "mimeType": "{{ $json.mimeType }}",
  "webContentLink": "{{ $json.webContentLink }}",
  "webViewLink": "{{ $json.webViewLink }}",
  "content": {{ $json.content }}
}
```

3. **OU use Form-URL-Encoded:**
   - kind: {{ $json.kind }}
   - id: {{ $json.id }}
   - name: {{ $json.name }}
   - mimeType: {{ $json.mimeType }}
   - webContentLink: {{ $json.webContentLink }}
   - webViewLink: {{ $json.webViewLink }}
   - content: {{ JSON.stringify($json.content) }}

**TESTE COM DADOS FIXOS PRIMEIRO:**
```json
{
  "kind": "drive#file",
  "id": "test123",
  "name": "teste.jpg",
  "mimeType": "image/jpeg",
  "webContentLink": "https://test.com",
  "webViewLink": "https://test.com",
  "content": {"parts": [{"text": "teste"}], "role": "model"}
}
```
