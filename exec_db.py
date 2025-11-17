import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
# Leer el archivo SQL
with open('init_sincro.sql', 'r') as f:
    sql_script = f.read()

DB_CONFIG = {
    'host':  os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSW'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT'))
}

# Conectar a MariaDB
conn = mysql.connector.connect(**DB_CONFIG)

cursor = conn.cursor()

# Ejecutar el script (separar por punto y coma si tiene múltiples statements)
for statement in sql_script.split(';'):
    if statement.strip():
        cursor.execute(statement)

conn.commit()
cursor.close()
conn.close()
