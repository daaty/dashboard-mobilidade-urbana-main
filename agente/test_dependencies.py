#!/usr/bin/env python3
"""
Teste rápido das dependências do deploy
"""

print("🔧 Testando importações críticas...")

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    print("✅ slowapi - OK")
except ImportError as e:
    print(f"❌ slowapi - {e}")

try:
    from cachetools import TTLCache
    print("✅ cachetools - OK")
except ImportError as e:
    print(f"❌ cachetools - {e}")

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
    print("✅ tenacity - OK")
except ImportError as e:
    print(f"❌ tenacity - {e}")

try:
    from fastapi import FastAPI
    print("✅ fastapi - OK")
except ImportError as e:
    print(f"❌ fastapi - {e}")

try:
    from pydantic import BaseModel, Field
    print("✅ pydantic - OK")
except ImportError as e:
    print(f"❌ pydantic - {e}")

try:
    import uvicorn
    print("✅ uvicorn - OK")
except ImportError as e:
    print(f"❌ uvicorn - {e}")

print("\n🎯 Teste das dependências completo!")
print("Se todas aparecem como ✅ OK, o deploy deve funcionar.")
