# CURL DINÂMICO PARA N8N - EXPRESSÕES CORRETAS

## 🎯 VERSÃO 1: DADOS DIRETOS (se o nó anterior retorna objeto direto)

```bash
curl -X POST \
  'https://agno.rotadoscelulares.com/financial/register' \
  -H 'Content-Type: application/json' \
  -d '{
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
  }'
```

## 🎯 VERSÃO 2: DADOS EM ARRAY (seus dados reais vêm como [0])

```bash
curl -X POST \
  'https://agno.rotadoscelulares.com/financial/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "kind": "{{ $json[0].kind }}",
    "id": "{{ $json[0].id }}",
    "name": "{{ $json[0].name }}",
    "mimeType": "{{ $json[0].mimeType }}",
    "webContentLink": "{{ $json[0].webContentLink }}",
    "webViewLink": "{{ $json[0].webViewLink }}",
    "content": {
      "parts": [
        {
          "text": "{{ $json[0].content.parts[0].text }}"
        }
      ],
      "role": "{{ $json[0].content.role }}"
    }
  }'
```

## 📝 COMO DESCOBRIR QUAL USAR:

1. **Olhe os dados do nó anterior** no N8N
2. Se aparecer como **objeto direto**: use VERSÃO 1
3. Se aparecer como **array [0]**: use VERSÃO 2

## 🔧 CONFIGURAÇÃO NO N8N:

### Método 1: Import cURL
1. HTTP Request Node → Menu "..." → Import cURL
2. Cole a versão correta
3. Pronto!

### Método 2: Manual (se import não funcionar)
**Method:** POST
**URL:** https://agno.rotadoscelulares.com/financial/register
**Body:** JSON
**JSON Body:** (cole o JSON da versão correta sem o curl)

## ⚠️ ATENÇÃO:

- **{{ $json.campo }}** = dados diretos
- **{{ $json[0].campo }}** = dados em array (primeiro elemento)
- **Aspas duplas são obrigatórias** nas expressions
- **Teste sempre** com dados reais primeiro

## 🧪 TESTE:

Depois de configurar, execute e verifique se:
1. ✅ Não dá erro de JSON
2. ✅ Recebe resposta 200
3. ✅ Gasto é registrado na tabela
