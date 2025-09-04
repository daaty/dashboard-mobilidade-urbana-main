import json

def count_cancelled_rides():
    # Ler o arquivo de dados adicionais
    with open('ADDITIONDATA', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total_driver_cancelled = 0
    total_user_cancelled = 0
    total_requests_received = 0
    total_success_rides = 0
    
    records_with_cancellations = []
    
    print("=== ANÁLISE DETALHADA DAS CORRIDAS CANCELADAS ===\n")
    
    for i, line in enumerate(lines[1:], 1):  # Pular o cabeçalho
        line = line.strip()
        if not line:
            continue
            
        try:
            data = json.loads(line)
            
            # Verificar se há cancelamentos
            driver_cancelled = 0
            user_cancelled = 0
            requests_received = 0
            success_rides = 0
            
            # Tentar diferentes formatos de chave
            if 'driver_cancelled_rides' in data:
                driver_cancelled = int(data['driver_cancelled_rides'])
            elif 'Driver Cancelled Rides' in data:
                driver_cancelled = int(data['Driver Cancelled Rides'])
                
            if 'user_cancelled_rides' in data:
                user_cancelled = int(data['user_cancelled_rides'])
            elif 'User Cancelled Rides' in data:
                user_cancelled = int(data['User Cancelled Rides'])
                
            if 'requests_received' in data:
                requests_received = int(data['requests_received'])
            elif 'Requests Received' in data:
                requests_received = int(data['Requests Received'])
                
            if 'success_rides' in data:
                success_rides = int(data['success_rides'])
            elif 'Success Rides' in data:
                success_rides = int(data['Success Rides'])
            
            # Acumular totais
            total_driver_cancelled += driver_cancelled
            total_user_cancelled += user_cancelled
            total_requests_received += requests_received
            total_success_rides += success_rides
            
            # Se há cancelamentos, mostrar detalhes
            if driver_cancelled > 0 or user_cancelled > 0:
                driver_name = data.get('Driver Name', data.get('driver_name', f'Driver {i}'))
                driver_id = data.get('Driver ID', data.get('driver_id', 'N/A'))
                
                print(f"Registro {i}:")
                print(f"  Driver: {driver_name} (ID: {driver_id})")
                print(f"  Corridas canceladas pelo motorista: {driver_cancelled}")
                print(f"  Corridas canceladas pelo usuário: {user_cancelled}")
                print(f"  Total de solicitações recebidas: {requests_received}")
                print(f"  Corridas concluídas com sucesso: {success_rides}")
                print()
                
                records_with_cancellations.append({
                    'driver_name': driver_name,
                    'driver_id': driver_id,
                    'driver_cancelled': driver_cancelled,
                    'user_cancelled': user_cancelled,
                    'requests_received': requests_received,
                    'success_rides': success_rides
                })
                
        except json.JSONDecodeError as e:
            print(f"Erro ao processar linha {i}: {e}")
            continue
    
    print("=== RESUMO FINAL ===")
    print(f"Total de corridas canceladas pelo motorista: {total_driver_cancelled}")
    print(f"Total de corridas canceladas pelo usuário: {total_user_cancelled}")
    print(f"Total de corridas canceladas (ambos): {total_driver_cancelled + total_user_cancelled}")
    print(f"Total de solicitações recebidas: {total_requests_received}")
    print(f"Total de corridas concluídas: {total_success_rides}")
    print(f"Total de registros com cancelamentos: {len(records_with_cancellations)}")
    
    # Calcular taxa de cancelamento
    if total_requests_received > 0:
        cancellation_rate = ((total_driver_cancelled + total_user_cancelled) / total_requests_received) * 100
        completion_rate = (total_success_rides / total_requests_received) * 100
        print(f"Taxa de cancelamento: {cancellation_rate:.2f}%")
        print(f"Taxa de conclusão: {completion_rate:.2f}%")

if __name__ == "__main__":
    count_cancelled_rides()
