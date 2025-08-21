#!/usr/bin/env python3
"""
Verificar os diferentes formatos de data entre scraper e Excel
"""
import asyncio
import sys
import os

# Adicionar o diretório backend ao path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from app.database.db import SessionLocal
from app.models.rides_data import RidesData
from sqlalchemy.future import select
import json
import re

async def verificar_formatos_data():
    async with SessionLocal() as session:
        # Buscar todos os registros
        result = await session.execute(select(RidesData))
        rides = result.scalars().all()
        
        print("="*80)
        print("🔍 ANÁLISE DOS FORMATOS DE DATA")
        print("="*80)
        
        for r in rides:
            ride_data = r.ride_data
            if isinstance(ride_data, str):
                try:
                    ride_data = json.loads(ride_data)
                except:
                    continue
            
            table_name = ride_data.get("tableName", "")
            source = r.source if hasattr(r, 'source') else 'N/A'
            new_records = ride_data.get("newRecords", [])
            
            print(f"\n📋 Tabela: {table_name}")
            print(f"🔗 Source: {source}")
            print(f"📊 Registros: {len(new_records)}")
            
            if table_name == "Completed Rides" and len(new_records) > 0:
                print(f"\n🗓️  FORMATOS DE DATA ENCONTRADOS:")
                
                # Analisar primeiros 3 registros para ver formato
                for i, rec in enumerate(new_records[:3]):
                    print(f"\n  📝 Registro {i+1}:")
                    print(f"     📋 Estrutura completa: {len(rec)} campos")
                    
                    # Verificar possíveis campos de data (índices 6, 7, 8)
                    for idx in range(6, min(len(rec), 12)):
                        if rec[idx] and str(rec[idx]).strip():
                            valor = str(rec[idx]).strip()
                            print(f"     [{idx:2d}] = '{valor}'")
                            
                            # Testar se parece com data
                            if re.search(r'\d{4}', valor):
                                # Teste formato scraper
                                scraper_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", valor)
                                if scraper_match:
                                    print(f"          ✅ FORMATO SCRAPER: {scraper_match.group(1)}")
                                
                                # Teste formato frontend
                                frontend_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", valor)
                                if frontend_match:
                                    print(f"          ✅ FORMATO FRONTEND: {frontend_match.group(1)}")
                                
                                if not scraper_match and not frontend_match:
                                    print(f"          ❌ FORMATO DESCONHECIDO!")
            
            print("-" * 60)

if __name__ == "__main__":
    asyncio.run(verificar_formatos_data())
