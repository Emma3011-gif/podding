"""Quick test of database connectivity"""
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

import models
print('models imported successfully')
print(f'DB_TYPE: {models.DB_TYPE}')
print(f'DATABASE_URL set: {bool(models.DATABASE_URL)}')

# Test connection
try:
    conn = models.get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT 1')
    result = cur.fetchone()
    print(f'Database connection test: {result}')
    conn.close()
    print('SUCCESS: PostgreSQL connection working!')
except Exception as e:
    print(f'Connection test failed: {e}')
