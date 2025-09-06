#!/usr/bin/env python3
"""
Teste direto das funções financeiras sem servidor
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "dashboard_agent"))

from dashboard_agent.tools.financial_tools import FinancialTools
import json

# Dados reais
financial_data = {
    "dados_extraidos": {
        "data_despesa": None,
        "valor_total": None,
        "descricao_item": "Página de erro 404",
        "tipo_documento": "Outro",
        "fornecedor": None
    },
    "descricao_imagem": "A imagem exibe uma página de erro 404 estilizada..."
}

def test_direct():
    """Teste direto da função"""
    print("🧪 TESTE DIRETO DAS FUNÇÕES FINANCEIRAS")
    print("=" * 50)
    
    try:
        # Inicializar
        financial_tools = FinancialTools()
        print("✅ FinancialTools inicializado")
        
        # Preparar dados
        dados_extraidos = financial_data["dados_extraidos"]
        
        data_despesa = dados_extraidos.get("data_despesa") or "2025-09-05"
        valor_total = dados_extraidos.get("valor_total")
        
        if valor_total is None:
            valor_total = 0.0
        else:
            try:
                valor_total = float(valor_total)
            except:
                valor_total = 0.0
        
        descricao_item = dados_extraidos.get("descricao_item", "Despesa não identificada")
        tipo_documento = dados_extraidos.get("tipo_documento", "Comprovante")
        fornecedor = dados_extraidos.get("fornecedor") or "Não identificado"
        
        descricao_imagem = financial_data["descricao_imagem"]
        arquivo_drive_url = "https://drive.google.com/uc?id=1OY3GUVQ_DQFg6FSzadSNFRDlKXBHB1y8&export=download"
        
        print("📄 DADOS PREPARADOS:")
        print(f"   - descricao_imagem: {descricao_imagem[:50]}...")
        print(f"   - arquivo_drive_url: {arquivo_drive_url}")
        print(f"   - data_despesa: {data_despesa}")
        print(f"   - valor_total: {valor_total}")
        print(f"   - descricao_item: {descricao_item}")
        print(f"   - tipo_documento: {tipo_documento}")
        print(f"   - fornecedor: {fornecedor}")
        print()
        
        # Chamar função
        result = financial_tools.inserir_gasto_empresa(
            descricao_imagem=descricao_imagem,
            arquivo_drive_url=arquivo_drive_url,
            data_despesa=data_despesa,
            valor_total=valor_total,
            descricao_item=descricao_item,
            tipo_documento=tipo_documento,
            fornecedor=fornecedor
        )
        
        print("✅ RESULTADO:")
        print(result)
        
        if "sucesso" in str(result).lower():
            print("\n🎉 FUNCIONOU! O gasto foi registrado com sucesso!")
            
            # Extrair ID se disponível
            import re
            id_match = re.search(r'ID[:\s]*(\d+)', str(result))
            if id_match:
                print(f"💾 ID do gasto: {id_match.group(1)}")
        else:
            print(f"\n❌ Erro no resultado: {result}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()
    
    print("\n" + "=" * 50)
    print("🔧 PRÓXIMOS PASSOS:")
    print("1. ✅ Função funciona diretamente")
    print("2. 🔄 Reiniciar servidor: Ctrl+C e python mobility_playground.py")
    print("3. 🧪 Testar endpoint novamente")
    print("4. 🎯 Configurar N8N com dados reais")
