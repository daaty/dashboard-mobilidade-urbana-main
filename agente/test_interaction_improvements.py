#!/usr/bin/env python3
"""
Teste das melhorias na interação do financial_endpoint
"""
import asyncio
import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.getcwd())

from financial_endpoint import handle_user_interaction

async def test_interactions():
    print('=== TESTE DAS MELHORIAS DE INTERAÇÃO ===\n')
    
    # Teste 1: Confirmação de fornecedor
    print('1. Teste confirmação de fornecedor:')
    result1 = await handle_user_interaction('Wesley', 'ta correto!')
    print(f'Resposta: {result1.message}\n')
    print('-' * 80)
    
    # Teste 2: Categoria alimentação
    print('2. Teste categoria alimentação:')
    result2 = await handle_user_interaction('Wesley', 'alimentacao')
    print(f'Resposta: {result2.message}\n')
    print('-' * 80)
    
    # Teste 3: Categoria com palavra relacionada
    print('3. Teste categoria com sinônimo:')
    result3 = await handle_user_interaction('Wesley', 'é comida')
    print(f'Resposta: {result3.message}\n')
    print('-' * 80)
    
    # Teste 4: Resposta sem NF
    print('4. Teste resposta sem NF:')
    result4 = await handle_user_interaction('Wesley', 'não possui NF')
    print(f'Resposta: {result4.message}\n')
    print('-' * 80)
    
    # Teste 5: Confirmação alternativa
    print('5. Teste confirmação alternativa:')
    result5 = await handle_user_interaction('Wesley', 'correto')
    print(f'Resposta: {result5.message}\n')
    print('-' * 80)
    
    # Teste 6: Mensagem não identificada curta
    print('6. Teste mensagem muito curta:')
    result6 = await handle_user_interaction('Wesley', 'ok')
    print(f'Resposta: {result6.message}\n')
    print('-' * 80)
    
    # Teste 7: Informação específica não identificada
    print('7. Teste informação específica não identificada:')
    result7 = await handle_user_interaction('Wesley', 'alguma informação específica')
    print(f'Resposta: {result7.message}\n')

if __name__ == "__main__":
    asyncio.run(test_interactions())
