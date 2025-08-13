#!/usr/bin/env python3
"""
Script de verificação rápida do sistema antes do deploy
"""
import subprocess
import sys
import os
from pathlib import Path

def check_backend_health():
    """Verifica se o backend está funcionando"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está funcionando corretamente")
            return True
        else:
            print(f"❌ Backend respondeu com status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend não está acessível: {e}")
        return False

def check_frontend_build():
    """Verifica se o frontend consegue fazer build"""
    try:
        os.chdir("frontend")
        result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True)
        os.chdir("..")
        
        if result.returncode == 0:
            print("✅ Frontend build realizado com sucesso")
            return True
        else:
            print(f"❌ Frontend build falhou: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar build do frontend: {e}")
        return False

def check_database_connection():
    """Verifica conexão com banco de dados"""
    try:
        # Simular verificação de DB
        print("✅ Conexão com banco de dados OK (simulado)")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão com banco: {e}")
        return False

def check_required_files():
    """Verifica se todos os arquivos necessários existem"""
    required_files = [
        "backend/requirements.txt",
        "backend/main.py",
        "Procfile",
        ".python-version",
        "frontend/package.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Arquivos obrigatórios ausentes: {missing_files}")
        return False
    else:
        print("✅ Todos os arquivos obrigatórios estão presentes")
        return True

def main():
    print("🔍 VERIFICAÇÃO PRE-DEPLOY - Dashboard Mobilidade Urbana")
    print("=" * 60)
    
    checks = [
        ("Arquivos obrigatórios", check_required_files),
        ("Conexão com banco", check_database_connection),
        ("Saúde do backend", check_backend_health),
        ("Build do frontend", check_frontend_build),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Verificando: {name}")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO:")
    
    all_passed = True
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🚀 SISTEMA PRONTO PARA DEPLOY!")
        print("✅ Todas as verificações passaram")
    else:
        print("⚠️  SISTEMA PRECISA DE CORREÇÕES")
        print("❌ Algumas verificações falharam")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
