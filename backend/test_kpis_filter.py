import requests

def test_kpis_filter():
    print('🧪 Testando KPIs - Todas as cidades...')
    response1 = requests.get('http://localhost:8000/api/drivers/kpis?period=30_days&city=all&status=all')
    data1 = response1.json()
    print(f'Status: {response1.status_code}')
    if data1.get('success'):
        kpis1 = data1["data"]
        print(f'Total motoristas (todas): {kpis1["total_drivers"]}')
        print(f'Receita total (todas): R$ {kpis1["total_revenue"]}')
        print(f'Corridas concluídas (todas): {kpis1["total_rides"]}')
        print(f'Corridas canceladas (todas): {kpis1["cancelled_rides"]}')
    else:
        print(f'Erro: {data1}')

    print()

    print('🧪 Testando KPIs - Nova Monte Verde...')
    response2 = requests.get('http://localhost:8000/api/drivers/kpis?period=30_days&city=Nova Monte Verde&status=all')
    data2 = response2.json()
    print(f'Status: {response2.status_code}')
    if data2.get('success'):
        kpis2 = data2["data"]
        print(f'Total motoristas (NMV): {kpis2["total_drivers"]}')
        print(f'Receita total (NMV): R$ {kpis2["total_revenue"]}')
        print(f'Corridas concluídas (NMV): {kpis2["total_rides"]}')
        print(f'Corridas canceladas (NMV): {kpis2["cancelled_rides"]}')
    else:
        print(f'Erro: {data2}')

if __name__ == "__main__":
    test_kpis_filter()
