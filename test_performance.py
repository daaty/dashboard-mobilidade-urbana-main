import sqlite3
import json

conn = sqlite3.connect('drivers_data.db')
cursor = conn.cursor()

# Verificar se há dados na aba Driver Performance
cursor.execute('SELECT COUNT(*) FROM drivers_data WHERE page_source = ?', ('Driver Performance',))
count = cursor.fetchone()[0]
print(f"Total registros Driver Performance: {count}")

if count > 0:
    # Pegar alguns exemplos
    cursor.execute('SELECT additional_data FROM drivers_data WHERE page_source = ? LIMIT 5', ('Driver Performance',))
    rows = cursor.fetchall()
    
    print("\nExemplos de dados:")
    for i, row in enumerate(rows):
        try:
            data = json.loads(row[0])
            online_hours = data.get('online_hours', 0)
            success_rides = data.get('success_rides', 0)
            print(f"Motorista {i+1}: {online_hours} horas online, {success_rides} corridas")
        except:
            print(f"Motorista {i+1}: Erro ao processar dados")

conn.close()
