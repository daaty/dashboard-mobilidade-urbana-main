#!/usr/bin/env python3
import sqlite3
import os

# Conectar ao banco de dados
db_path = './instance/mobilidade_urbana_dev.db'
if not os.path.exists(db_path):
    print(f"Banco de dados não encontrado em: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Listar tabelas disponíveis
print("=== TABELAS DISPONÍVEIS ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

print("\n" + "="*80)

# Se a tabela gastos_empresa existir, consultar os dados
try:
    cursor.execute("SELECT COUNT(*) FROM gastos_empresa")
    count = cursor.fetchone()[0]
    print(f"\nTotal de registros na tabela gastos_empresa: {count}")
    
    if count > 0:
        print("\n=== ESTRUTURA DOS DADOS ===")
        cursor.execute("""
            SELECT id, data_despesa, valor_total, descricao_item, tipo_documento, 
                   fornecedor, id_documento_vinculado, numero_nota_fiscal, arquivo_drive_url
            FROM gastos_empresa 
            ORDER BY data_despesa DESC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        
        print("ID | Data | Valor | Descrição | Tipo | Fornecedor | ID_Vinculado | NF_Numero | URL")
        print("-" * 120)
        
        for row in rows:
            desc = (row[3][:15] + '...') if row[3] and len(row[3]) > 15 else (row[3] or 'N/A')
            forn = (row[5][:15] + '...') if row[5] and len(row[5]) > 15 else (row[5] or 'N/A')
            url = 'SIM' if row[8] else 'NÃO'
            print(f"{row[0]} | {row[1]} | {row[2]} | {desc} | {row[4]} | {forn} | {row[6]} | {row[7]} | {url}")
        
        # Verificar documentos vinculados
        print("\n=== ANÁLISE DE DOCUMENTOS VINCULADOS ===")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN id_documento_vinculado IS NOT NULL THEN 1 END) as com_vinculo,
                COUNT(CASE WHEN tipo_documento = 'Nota Fiscal' THEN 1 END) as notas_fiscais,
                COUNT(CASE WHEN tipo_documento = 'Comprovante de Pagamento' THEN 1 END) as comprovantes
            FROM gastos_empresa
        """)
        stats = cursor.fetchone()
        print(f"Total de registros: {stats[0]}")
        print(f"Com documento vinculado: {stats[1]}")
        print(f"Notas Fiscais: {stats[2]}")
        print(f"Comprovantes de Pagamento: {stats[3]}")
        
        # Verificar pares de documentos
        print("\n=== PARES DE DOCUMENTOS ===")
        cursor.execute("""
            SELECT nf.id as nf_id, nf.descricao_item as nf_desc, nf.valor_total as nf_valor,
                   comp.id as comp_id, comp.descricao_item as comp_desc, comp.valor_total as comp_valor,
                   nf.data_despesa, nf.fornecedor
            FROM gastos_empresa nf
            JOIN gastos_empresa comp ON nf.id = comp.id_documento_vinculado
            WHERE nf.tipo_documento = 'Nota Fiscal' 
            AND comp.tipo_documento = 'Comprovante de Pagamento'
            ORDER BY nf.data_despesa DESC
        """)
        pairs = cursor.fetchall()
        
        if pairs:
            print("NF_ID | NF_Descrição | NF_Valor | COMP_ID | COMP_Descrição | COMP_Valor | Data | Fornecedor")
            print("-" * 120)
            for pair in pairs:
                nf_desc = (pair[1][:15] + '...') if pair[1] and len(pair[1]) > 15 else (pair[1] or 'N/A')
                comp_desc = (pair[4][:15] + '...') if pair[4] and len(pair[4]) > 15 else (pair[4] or 'N/A')
                forn = (pair[7][:15] + '...') if pair[7] and len(pair[7]) > 15 else (pair[7] or 'N/A')
                print(f"{pair[0]} | {nf_desc} | {pair[2]} | {pair[3]} | {comp_desc} | {pair[5]} | {pair[6]} | {forn}")
        else:
            print("Nenhum par de documentos encontrado")

except sqlite3.OperationalError as e:
    print(f"Erro: {e}")

conn.close()
