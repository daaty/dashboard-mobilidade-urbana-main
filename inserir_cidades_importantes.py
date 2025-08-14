#!/usr/bin/env python3
"""Script para criar as 3 cidades importantes na tabela de demografia"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database.db import SessionLocal
from app.models.cidades_demografia import CidadesDemografia

def main():
    print("🏗️ CRIANDO CIDADES IMPORTANTES")
    print("=" * 50)
    
    # Dados das 3 cidades importantes
    cidades_importantes = [
        {
            'cidade': 'MATUPA', 
            'populacao_censo_2022': 15000, 
            'populacao_estimada_2024': 15000, 
            'publico_alvo_15_44_anos': 6600
        },
        {
            'cidade': 'PEIXOTO', 
            'populacao_censo_2022': 12000, 
            'populacao_estimada_2024': 12000, 
            'publico_alvo_15_44_anos': 5280
        },
        {
            'cidade': 'GUARANTA DO NORTE', 
            'populacao_censo_2022': 8000, 
            'populacao_estimada_2024': 8000, 
            'publico_alvo_15_44_anos': 3520
        }
    ]

    db = SessionLocal()
    try:
        for cidade_data in cidades_importantes:
            # Verificar se já existe
            nome_cidade = cidade_data['cidade']
            exists = db.query(CidadesDemografia).filter(CidadesDemografia.cidade == nome_cidade).first()
            
            if not exists:
                cidade = CidadesDemografia(**cidade_data)
                db.add(cidade)
                print(f'✅ Criada cidade: {nome_cidade}')
            else:
                print(f'⚠️ Cidade já existe: {nome_cidade} (ID: {exists.id})')
        
        db.commit()
        print('🎉 Processo concluído!')
        
        # Listar todas as cidades
        print("\n📊 CIDADES NA TABELA:")
        cidades = db.query(CidadesDemografia).all()
        print(f'Total: {len(cidades)} cidades')
        for c in cidades:
            pop_formatada = f"{c.populacao_censo_2022:,}" if c.populacao_censo_2022 else "N/A"
            print(f'   {c.id}: {c.cidade} (pop: {pop_formatada})')
            
    except Exception as e:
        print(f'❌ Erro: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
