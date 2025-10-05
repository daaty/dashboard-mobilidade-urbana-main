import psycopg2
import json

c = psycopg2.connect(host='148.230.73.27', port=5432, database='n8n_db', user='n8n_user', password='n8n_pw')
cur = c.cursor()

print("\n" + "="*80)
print("VERIFICAÇÃO: STATUS NA TABELA driver_personal_details")
print("="*80)
print()

# Verificar quantos motoristas têm cada status
cur.execute("""
    SELECT 
        personal_data->>'status' as status,
        COUNT(*) as quantidade
    FROM driver_personal_details
    WHERE personal_data IS NOT NULL
    GROUP BY personal_data->>'status'
    ORDER BY COUNT(*) DESC;
""")

results = cur.fetchall()

print("STATUS ENCONTRADOS:")
print("-" * 50)
total_ativos = 0
for row in results:
    status = row[0] if row[0] else "NULL"
    qtd = row[1]
    
    # Considerar ATIVOS: Active, Online, Offline, Busy
    if status.lower() in ['active', 'online', 'offline', 'busy']:
        total_ativos += qtd
        print(f"✅ {status}: {qtd} motoristas (ATIVO)")
    else:
        print(f"❌ {status}: {qtd} motoristas (INATIVO/UNKNOWN)")

print("-" * 50)
print(f"\n📊 TOTAL DE MOTORISTAS ATIVOS: {total_ativos}")
print(f"   (Status em: Active, Online, Offline, Busy)")
print()
print("="*80)

cur.close()
c.close()
