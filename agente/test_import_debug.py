"""
Teste simples para identificar problema de importação
"""

print("🔧 Teste 1: Importações básicas...")
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date
print("✅ Importações básicas OK")

print("🔧 Teste 2: Importações AGNO...")
from agno.tools import Toolkit
from agno.utils.log import logger
print("✅ Importações AGNO OK")

print("🔧 Teste 3: Criando classe básica...")
class TestTool(Toolkit):
    def __init__(self, **kwargs):
        tools = [self.test_method]
        super().__init__(name="test_tool", tools=tools, **kwargs)
    
    def test_method(self):
        return "teste"

print("✅ Classe TestTool criada OK")

print("🔧 Teste 4: Instanciando classe...")
tool = TestTool()
print("✅ Instância criada OK")

print("🔧 Teste 5: Testando método...")
result = tool.test_method()
print(f"✅ Método executado: {result}")

print("🎉 Todos os testes passaram!")
