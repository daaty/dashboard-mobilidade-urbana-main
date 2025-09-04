import sqlite3
import json

def check_driver_17147322():
    try:
        conn = sqlite3.connect('drivers_data.db')
        cursor = conn.cursor()

        # Buscar driver com ID 17147322 que tem cancelamentos
        cursor.execute('SELECT * FROM driver_personal_details WHERE driver_id = ?', ('17147322',))
        result = cursor.fetchone()

        if result:
            columns = [description[0] for description in cursor.description]
            driver_data = dict(zip(columns, result))
            print('Driver 17147322 personal details:')
            for key, value in driver_data.items():
                print(f'  {key}: {value}')
        else:
            print('Driver 17147322 não encontrado em driver_personal_details')

        # Buscar na drivers_data também
        cursor.execute('SELECT driver_id, name, page_source, additional_data FROM drivers_data WHERE driver_id = ?', ('17147322',))
        results = cursor.fetchall()

        if results:
            print('\nDriver 17147322 em drivers_data:')
            for result in results:
                print(f'  ID: {result[0]}, Nome: {result[1]}, Page: {result[2]}')
                if result[3]:
                    try:
                        additional = json.loads(result[3])
                        print(f'  Additional data: {additional}')
                    except:
                        print(f'  Additional data (raw): {result[3]}')

        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_driver_17147322()
