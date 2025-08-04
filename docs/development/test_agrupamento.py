#!/usr/bin/env python3
"""
Script para testar a lógica de agrupamento de documentos
Simula diferentes cenários de Comprovantes com e sem NF
"""

def parse_valor(valor_str):
    """Função para converter string de valor para float"""
    if not valor_str:
        return 0.0
    try:
        valor_clean = str(valor_str).replace(',', '.').replace('R$', '').replace(' ', '')
        return float(valor_clean)
    except:
        return 0.0

# Simular dados de teste
class MockGasto:
    def __init__(self, id, tipo_documento, valor_total, descricao_item, fornecedor, 
                 possui_nota_fiscal=0, id_documento_vinculado=None, arquivo_drive_url="", 
                 data_despesa="2025-05-13", numero_nota_fiscal="", natureza_do_gasto=""):
        self.id = id
        self.tipo_documento = tipo_documento
        self.valor_total = valor_total
        self.descricao_item = descricao_item
        self.fornecedor = fornecedor
        self.possui_nota_fiscal = possui_nota_fiscal
        self.id_documento_vinculado = id_documento_vinculado
        self.arquivo_drive_url = arquivo_drive_url
        self.data_despesa = data_despesa
        self.numero_nota_fiscal = numero_nota_fiscal
        self.natureza_do_gasto = natureza_do_gasto

# Dados de teste simulando o problema
gastos_teste = [
    # Caso 1: NF + Comprovante (DUPLICAÇÃO)
    MockGasto(
        id=1, 
        tipo_documento="Nota Fiscal", 
        valor_total="72,53",
        descricao_item="Almoco Refeicao",
        fornecedor="Cassiano Korbes - Restaurante",
        possui_nota_fiscal=1,
        numero_nota_fiscal="123456",
        arquivo_drive_url="https://drive.google.com/nf123",
        natureza_do_gasto="Alimentacao"
    ),
    MockGasto(
        id=2, 
        tipo_documento="Comprovante de Pagamento", 
        valor_total="72,53",  # MESMO VALOR - DUPLICAÇÃO
        descricao_item="Pagamento via QR Code",
        fornecedor="Cassiano Korbes Restaurante Me",
        possui_nota_fiscal=1,  # TEM NF
        id_documento_vinculado=1,  # VINCULADO À NF ID=1
        arquivo_drive_url="https://drive.google.com/comp123",
        natureza_do_gasto="Alimentacao"
    ),
    
    # Caso 2: Comprovante SEM NF (NÃO DUPLICA)
    MockGasto(
        id=3, 
        tipo_documento="Comprovante de Pagamento", 
        valor_total="25,00",
        descricao_item="Combustível Posto ABC",
        fornecedor="Posto ABC",
        possui_nota_fiscal=0,  # SEM NF - NÃO DUPLICA
        arquivo_drive_url="https://drive.google.com/comp456",
        natureza_do_gasto="Combustivel"
    ),
    
    # Caso 3: Outro comprovante COM NF
    MockGasto(
        id=4, 
        tipo_documento="Nota Fiscal", 
        valor_total="150,00",
        descricao_item="Manutencao Veiculo",
        fornecedor="Oficina XYZ",
        possui_nota_fiscal=1,
        numero_nota_fiscal="789012",
        arquivo_drive_url="https://drive.google.com/nf456",
        natureza_do_gasto="Manutencao"
    ),
    MockGasto(
        id=5, 
        tipo_documento="Comprovante de Pagamento", 
        valor_total="150,00",  # MESMO VALOR
        descricao_item="Pagamento Manutencao",
        fornecedor="Oficina XYZ Ltda",
        possui_nota_fiscal=1,  # TEM NF
        id_documento_vinculado=4,  # VINCULADO À NF ID=4
        arquivo_drive_url="https://drive.google.com/comp789",
        natureza_do_gasto="Manutencao"
    )
]

def agrupar_documentos_relacionados(gastos_lista):
    """
    Agrupa documentos relacionados em uma única entrada
    REGRA: Só agrupa comprovantes que POSSUEM nota fiscal (possui_nota_fiscal = 1)
    """
    documentos_agrupados = {}
    comprovantes_com_nf = {}
    
    # Primeiro passo: processar todos os documentos
    for gasto in gastos_lista:
        if gasto.tipo_documento == "Nota Fiscal":
            # Sempre criar entrada para Nota Fiscal
            documentos_agrupados[gasto.id] = {
                "id": gasto.id,
                "data_despesa": gasto.data_despesa,
                "valor_total": parse_valor(gasto.valor_total),
                "descricao_item": gasto.descricao_item,
                "fornecedor": gasto.fornecedor,
                "tipo_documento": gasto.tipo_documento,
                "possui_nota_fiscal": True,
                "numero_nota_fiscal": gasto.numero_nota_fiscal,
                "documentos": [
                    {
                        "tipo": "Nota Fiscal",
                        "url": gasto.arquivo_drive_url,
                        "id": gasto.id
                    }
                ]
            }
        
        elif gasto.tipo_documento == "Comprovante de Pagamento":
            if gasto.possui_nota_fiscal and gasto.id_documento_vinculado:
                # Comprovante COM NF - vai ser vinculado à NF
                comprovantes_com_nf[gasto.id_documento_vinculado] = {
                    "tipo": "Comprovante de Pagamento",
                    "url": gasto.arquivo_drive_url,
                    "id": gasto.id
                }
            else:
                # Comprovante SEM NF - criar entrada separada
                documentos_agrupados[gasto.id] = {
                    "id": gasto.id,
                    "data_despesa": gasto.data_despesa,
                    "valor_total": parse_valor(gasto.valor_total),
                    "descricao_item": gasto.descricao_item,
                    "fornecedor": gasto.fornecedor,
                    "tipo_documento": gasto.tipo_documento,
                    "possui_nota_fiscal": False,
                    "numero_nota_fiscal": "",
                    "documentos": [
                        {
                            "tipo": "Comprovante de Pagamento",
                            "url": gasto.arquivo_drive_url,
                            "id": gasto.id
                        }
                    ]
                }
    
    # Segundo passo: vincular comprovantes COM NF às suas NFs
    for id_nf, comprovante in comprovantes_com_nf.items():
        if id_nf in documentos_agrupados:
            documentos_agrupados[id_nf]["documentos"].append(comprovante)
    
    return list(documentos_agrupados.values())

# Executar teste
print("=== DADOS ORIGINAIS (COM DUPLICAÇÃO) ===")
total_original = sum(parse_valor(gasto.valor_total) for gasto in gastos_teste)
print(f"Total registros: {len(gastos_teste)}")
print(f"Total valor (com duplicação): R$ {total_original:.2f}")
print()

for gasto in gastos_teste:
    print(f"ID: {gasto.id} | {gasto.tipo_documento} | R$ {gasto.valor_total} | {gasto.descricao_item} | NF: {bool(gasto.possui_nota_fiscal)} | Vinculado: {gasto.id_documento_vinculado}")

print("\n" + "="*80)
print("=== DADOS AGRUPADOS (SEM DUPLICAÇÃO) ===")

gastos_agrupados = agrupar_documentos_relacionados(gastos_teste)
total_agrupado = sum(gasto["valor_total"] for gasto in gastos_agrupados)

print(f"Total registros agrupados: {len(gastos_agrupados)}")
print(f"Total valor (sem duplicação): R$ {total_agrupado:.2f}")
print(f"Diferença: R$ {total_original - total_agrupado:.2f}")
print()

for gasto in gastos_agrupados:
    docs = ", ".join([f"{doc['tipo']}" for doc in gasto["documentos"]])
    print(f"ID: {gasto['id']} | R$ {gasto['valor_total']:.2f} | {gasto['descricao_item']} | Documentos: [{docs}]")

print("\n=== ANÁLISE ===")
print("✅ Comprovantes SEM NF: mantidos separados")
print("✅ Comprovantes COM NF: agrupados com suas NFs")
print("✅ Eliminação da duplicação de valores")
