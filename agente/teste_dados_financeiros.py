#!/usr/bin/env python3
"""
Script para testar o agente com dados financeiros simulando o n8n
"""
import json
import requests

# Dados exatos que o agente receberá do n8n
dados_exemplo = {
    "kind": "drive#file",
    "id": "1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8",
    "name": "comprovante_outro_20250905_203546.jpg",
    "mimeType": "text/html",
    "webContentLink": "https://drive.google.com/uc?id=1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8&export=download",
    "webViewLink": "https://drive.google.com/file/d/1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8/view?usp=drivesdk",
    "content": {
        "parts": [
            {
                "text": '''```json
{
  "dados_extraidos": {
    "data_despesa": "2025-09-05",
    "valor_total": 150.75,
    "descricao_item": "Combustível para veículo da empresa",
    "tipo_documento": "Comprovante",
    "fornecedor": "Posto Shell"
  },
  "descricao_imagem": "Comprovante de pagamento de combustível no Posto Shell. Data: 05/09/2025. Valor: R$ 150,75. Produto: Gasolina comum. Placa do veículo: ABC-1234."
}
```'''
            }
        ],
        "role": "model"
    }
}

# Extrair dados para enviar ao agente
descricao_arquivo = dados_exemplo["content"]["parts"][0]["text"]
link_arquivo = dados_exemplo["webContentLink"]

# Mensagem que será enviada ao agente (simula o que vem do n8n)
mensagem_financeira = f"""
DADOS RECEBIDOS PARA REGISTRO FINANCEIRO:

DESCRIÇÃO DO ARQUIVO: {descricao_arquivo}

LINK DO ARQUIVO: {link_arquivo}

Por favor, processe estes dados e registre na tabela de gastos da empresa.
"""

print("📄 SIMULAÇÃO DE DADOS FINANCEIROS DO N8N")
print("=" * 60)
print()
print("🔧 Dados que o agente receberá:")
print(f"📋 Nome do arquivo: {dados_exemplo['name']}")
print(f"🔗 Link do arquivo: {link_arquivo}")
print(f"📄 Descrição extraída: {descricao_arquivo[:100]}...")
print()
print("💬 Mensagem que será enviada ao agente:")
print("-" * 40)
print(mensagem_financeira)
print("-" * 40)
print()
print("🚀 Para testar, envie esta mensagem no playground AGNO:")
print("https://app.agno.com/playground?endpoint=0.0.0.0%3A8001/v1")
print()
print("✅ O agente deve reconhecer automaticamente e executar o fluxo financeiro!")

# Salvar em arquivo para fácil cópia
with open("teste_dados_financeiros.txt", "w", encoding="utf-8") as f:
    f.write(mensagem_financeira)

print()
print("💾 Mensagem salva em: teste_dados_financeiros.txt")
