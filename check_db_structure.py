import sqlite3

def check_tables():
    try:
        conn = sqlite3.connect('drivers_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print('Tabelas disponíveis:')
        for table in tables:
            print(f'  {table[0]}')
        
        # Verificar estrutura da tabela drivers_data
        cursor.execute('PRAGMA table_info(drivers_data)')
        columns = cursor.fetchall()
        print('\nColunas da tabela drivers_data:')
        for col in columns:
            print(f'  {col[1]} ({col[2]})')
            
        # Buscar driver 17147322
        cursor.execute('SELECT driver_id, name, page_source, additional_data FROM drivers_data WHERE driver_id = ? LIMIT 3', ('17147322',))
        results = cursor.fetchall()
        
        print(f'\nDriver 17147322 encontrado {len(results)} vezes:')
        for i, result in enumerate(results):
            print(f'  Registro {i+1}: ID={result[0]}, Nome={result[1]}, Page={result[2]}')
            
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_tables()
