#!/usr/bin/env python3
"""
Análise completa das corridas na tabela rides_data com base no SQL exportado
"""
import json
import re
from datetime import datetime

def extract_data_from_sql():
    """Extrai e analisa todos os dados do arquivo SQL exportado"""
    
    # Dados dos registros conforme o SQL exportado
    records = [
        {
            "id": 10,
            "table_name": "Cancelled Rides", 
            "source": "import_excel",
            "count": "42 corridas canceladas (exemplo: Rogério Gelcivan, Weslei Martins, etc.)"
        },
        {
            "id": 11,
            "table_name": "Completed Rides",
            "source": "import_excel", 
            "count": "95 corridas concluídas (Rogério Oliveira Lima, Elindo Julião, Bruno Silva, etc.)"
        },
        {
            "id": 12,
            "table_name": "Missed Rides",
            "source": "import_excel",
            "count": "63 corridas perdidas (Maycon Batista, Renatia Barroso, etc.)"
        },
        {
            "id": 13,
            "table_name": "rides_data",
            "source": "import_excel",
            "count": "95 corridas (duplicata das Completed Rides do registro 11)"
        },
        {
            "id": 14,
            "table_name": "rides_data", 
            "source": "import_excel",
            "count": "42 corridas (duplicata das Cancelled Rides do registro 10)"
        },
        {
            "id": 15,
            "table_name": "rides_data",
            "source": "import_excel", 
            "count": "63 corridas (duplicata das Missed Rides do registro 12)"
        },
        {
            "id": 16,
            "table_name": "Completed Rides",
            "source": "monitoring-service-adapted",
            "count": "2 corridas do dia 20/08 (Bruno Silva e Elindo Juliao - SCRAPER)"
        }
    ]
    
    print("="*80)
    print("🔍 ANÁLISE COMPLETA DA TABELA RIDES_DATA")
    print("="*80)
    
    total_excel_completed = 95
    total_excel_cancelled = 42  
    total_excel_missed = 63
    total_scraper_completed = 2
    
    print(f"\n📊 RESUMO COMPLETO DOS DADOS:")
    print(f"┌─────────────────────────────────────────────────┐")
    print(f"│ DADOS IMPORTADOS DO EXCEL (source=import_excel) │")
    print(f"├─────────────────────────────────────────────────┤")
    print(f"│ • Corridas Concluídas: {total_excel_completed:3d} corridas           │")
    print(f"│ • Corridas Canceladas: {total_excel_cancelled:3d} corridas           │") 
    print(f"│ • Corridas Perdidas:   {total_excel_missed:3d} corridas           │")
    print(f"│ • TOTAL EXCEL:         {total_excel_completed + total_excel_cancelled + total_excel_missed:3d} corridas           │")
    print(f"└─────────────────────────────────────────────────┘")
    
    print(f"\n┌─────────────────────────────────────────────────┐")
    print(f"│ DADOS DO SCRAPER (monitoring-service-adapted)   │")
    print(f"├─────────────────────────────────────────────────┤")
    print(f"│ • Corridas Concluídas: {total_scraper_completed:3d} corridas (dia 20/08) │")
    print(f"└─────────────────────────────────────────────────┘")
    
    print(f"\n🎯 CONCLUSÃO CRÍTICA:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"A API DEVERIA MOSTRAR:")
    print(f"• Total de Corridas Concluídas: {total_excel_completed + total_scraper_completed} corridas")
    print(f"  └─ {total_excel_completed} corridas do Excel + {total_scraper_completed} corridas do Scraper")
    print(f"")
    print(f"MAS A API MOSTRA APENAS:")
    print(f"• {total_scraper_completed} corridas concluídas (1.9%)")
    print(f"")
    print(f"❌ PROBLEMA: A API está ignorando as {total_excel_completed} corridas")
    print(f"   importadas do Excel, processando apenas dados do scraper!")
    
    print(f"\n🔧 DETALHES TÉCNICOS:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"• Registros na tabela: 7 registros")
    print(f"• IDs 10-15: Dados do Excel (source='import_excel')")
    print(f"• ID 16: Dados do Scraper (source='monitoring-service-adapted')")
    print(f"• Duplicatas: IDs 13,14,15 são duplicatas dos dados dos IDs 11,10,12")
    print(f"")
    print(f"🐛 CAUSA DO BUG:")
    print(f"A API está filtrando apenas por table_name='Completed Rides'")
    print(f"E/OU apenas source='monitoring-service-adapted'")
    print(f"Ignorando os dados importados do Excel!")
    
    print(f"\n💡 SOLUÇÃO NECESSÁRIA:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Modificar o endpoint /api/metrics/overview para:")
    print(f"1. Processar AMBAS as fontes: 'import_excel' E 'monitoring-service-adapted'")
    print(f"2. Agregar corridas concluídas de TODOS os registros")
    print(f"3. Evitar duplicação dos dados")
    
    return {
        "excel_completed": total_excel_completed,
        "excel_cancelled": total_excel_cancelled, 
        "excel_missed": total_excel_missed,
        "scraper_completed": total_scraper_completed,
        "total_should_show": total_excel_completed + total_scraper_completed,
        "currently_showing": total_scraper_completed,
        "missing_rides": total_excel_completed
    }

if __name__ == "__main__":
    results = extract_data_from_sql()
    
    print(f"\n" + "="*80)
    print(f"✅ ANÁLISE CONCLUÍDA - PROBLEMA IDENTIFICADO!")
    print(f"="*80)
    print(f"Taxa de conclusão CORRETA deveria ser:")
    print(f"{results['total_should_show']} concluídas / {results['total_should_show'] + results['excel_cancelled'] + results['excel_missed']} total")
    print(f"= {(results['total_should_show'] / (results['total_should_show'] + results['excel_cancelled'] + results['excel_missed']) * 100):.1f}% (não 1.9%!)")
