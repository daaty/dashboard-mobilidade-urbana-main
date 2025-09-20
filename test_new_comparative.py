import requests
import json

# Testar o novo endpoint comparative
url = "http://localhost:8000/api/metrics/comparative"
params = {
    "periodo": "6",
    "cidade": "Sorocaba"
}

print("🚀 TESTANDO NOVO ENDPOINT COMPARATIVE...")
print(f"URL: {url}")
print(f"Params: {params}")
print("="*50)

try:
    response = requests.get(url, params=params)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ RESPOSTA RECEBIDA!")
        print("\n📊 ESTRUTURA DA RESPOSTA:")
        print(f"- success: {data.get('success')}")
        print(f"- periodo_meses: {data.get('periodo_meses')}")
        print(f"- cidade: {data.get('cidade')}")
        print(f"- total_records: {data.get('total_records')}")
        print(f"- meses_analisados: {data.get('meses_analisados')}")
        
        # Verificar months_metadata
        months_metadata = data.get('months_metadata', [])
        print(f"\n🗓️ METADADOS DOS MESES ({len(months_metadata)} meses):")
        for month in months_metadata:
            print(f"  - {month.get('label')}: {month.get('total_geral')} corridas total")
            print(f"    ✅ Concluídas: {month.get('total_concluidas')}")
            print(f"    ❌ Canceladas: {month.get('total_canceladas')}")
            print(f"    ⏰ Perdidas: {month.get('total_perdidas')}")
        
        # Verificar daily_data (alguns dias)
        daily_data = data.get('daily_data', [])
        print(f"\n📈 DADOS DIÁRIOS (mostrando primeiros 5 dias de {len(daily_data)}):")
        for i, day_data in enumerate(daily_data[:5]):
            dia = day_data.get('day')
            print(f"\n  📅 DIA {dia}:")
            
            # Mostrar dados de cada mês para este dia
            for key, value in day_data.items():
                if key.endswith('_total') and value > 0:
                    mes_key = key.replace('_total', '')
                    nome_mes = day_data.get(f'{mes_key}_nome', 'N/A')
                    concluidas = day_data.get(f'{mes_key}_concluidas', 0)
                    print(f"    {nome_mes}: {value} corridas ({concluidas} concluídas)")
        
        # Verificar se há dados reais
        total_geral = sum(month.get('total_geral', 0) for month in months_metadata)
        print(f"\n📊 RESUMO GERAL:")
        print(f"Total de corridas encontradas: {total_geral}")
        
        if total_geral > 0:
            print("🎉 SUCESSO! Endpoint retornando dados reais!")
        else:
            print("⚠️ AVISO: Endpoint retornando apenas zeros")
            
    else:
        print(f"❌ ERRO: Status {response.status_code}")
        print(f"Resposta: {response.text}")
        
except Exception as e:
    print(f"❌ ERRO na requisição: {e}")