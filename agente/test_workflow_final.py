#!/usr/bin/env python3
"""
Teste final das melhorias na interação - cenário completo
"""
import asyncio
import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.getcwd())

from financial_endpoint import handle_user_interaction

async def test_complete_workflow():
    print('=== TESTE DO WORKFLOW COMPLETO REFINADO ===\n')
    
    print("🔴 SIMULANDO CONVERSA APÓS REGISTRO DE IMAGEM:")
    print("(Sistema já processou imagem e perguntou sobre NF, categoria e fornecedor)\n")
    
    # Teste 1: Usuário responde sobre NF
    print('👤 Wesley: "é alimentação, nao possui NF"')
    result1 = await handle_user_interaction('Wesley', 'é alimentação, nao possui NF')
    print(f'🤖 Alice: {result1.message}\n')
    print('-' * 100)
    
    # Teste 2: Usuário especifica categoria
    print('👤 Wesley: "alimentacao"')
    result2 = await handle_user_interaction('Wesley', 'alimentacao')
    print(f'🤖 Alice: {result2.message}\n')
    print('-' * 100)
    
    # Teste 3: Usuário confirma fornecedor
    print('👤 Wesley: "ta correto!"')
    result3 = await handle_user_interaction('Wesley', 'ta correto!')
    print(f'🤖 Alice: {result3.message}\n')
    print('-' * 100)
    
    print("\n🔵 TESTANDO OUTROS CENÁRIOS:")
    
    # Teste 4: Usuário corrige fornecedor
    print('👤 Wesley: "Restaurante do João"')
    result4 = await handle_user_interaction('Wesley', 'Restaurante do João')
    print(f'🤖 Alice: {result4.message}\n')
    print('-' * 100)
    
    # Teste 5: Confirmação simples
    print('👤 Wesley: "ok"')
    result5 = await handle_user_interaction('Wesley', 'ok')
    print(f'🤖 Alice: {result5.message}\n')
    print('-' * 100)
    
    # Teste 6: Categoria com sinônimo
    print('👤 Wesley: "é comida"')
    result6 = await handle_user_interaction('Wesley', 'é comida')
    print(f'🤖 Alice: {result6.message}\n')

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
