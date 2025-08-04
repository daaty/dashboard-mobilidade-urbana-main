import asyncio
import sys
sys.path.append('.')
from app.api.financeiro import get_financeiro_overview
from app.database.db import SessionLocal

async def test_financeiro():
    async with SessionLocal() as db:
        # Primeiro, modificar a API para aceitar período personalizado
        print("=== Testando API Financeira com dados de maio ===")
        
        # Modificar temporariamente a API para não filtrar por data
        from sqlalchemy import select
        from app.models.gastos_empresa import GastosEmpresa
        
        # Buscar TODOS os registros sem filtro de data
        all_result = await db.execute(select(GastosEmpresa))
        all_records = all_result.scalars().all()
        
        print(f"Total de registros encontrados: {len(all_records)}")
        
        if all_records:
            # Processar manualmente os dados
            total_gastos = 0
            gastos_por_categoria = {}
            gastos_por_fornecedor = {}
            documentacao_stats = {"com_nota": 0, "sem_nota": 0}
            
            for record in all_records:
                valor = float(record.valor_total) if record.valor_total else 0
                total_gastos += valor
                
                # Categoria
                categoria = record.natureza_do_gasto or 'Outros'
                gastos_por_categoria[categoria] = gastos_por_categoria.get(categoria, 0) + valor
                
                # Fornecedor
                fornecedor = record.fornecedor or 'Não informado'
                gastos_por_fornecedor[fornecedor] = gastos_por_fornecedor.get(fornecedor, 0) + valor
                
                # Documentação
                if record.possui_nota_fiscal:
                    documentacao_stats["com_nota"] += 1
                else:
                    documentacao_stats["sem_nota"] += 1
            
            print(f"Total de gastos: R$ {total_gastos:.2f}")
            print(f"Total de transações: {len(all_records)}")
            taxa_doc = (documentacao_stats['com_nota'] / len(all_records) * 100) if len(all_records) > 0 else 0
            print(f"Taxa de documentação: {taxa_doc:.1f}%")
            
            if gastos_por_categoria:
                print("\nCategorias encontradas:")
                for cat, valor in gastos_por_categoria.items():
                    print(f"  {cat}: R$ {valor:.2f}")
            
            if gastos_por_fornecedor:
                print("\nFornecedores encontrados:")
                for forn, valor in gastos_por_fornecedor.items():
                    print(f"  {forn}: R$ {valor:.2f}")
            
            print(f"\nDocumentação:")
            print(f"  Com nota fiscal: {documentacao_stats['com_nota']}")
            print(f"  Sem nota fiscal: {documentacao_stats['sem_nota']}")

if __name__ == "__main__":
    asyncio.run(test_financeiro())
