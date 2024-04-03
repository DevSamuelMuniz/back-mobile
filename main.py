import sqlite3

conn = sqlite3.connect('postComidas.db')

cursor = conn.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS postComidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    foto BLOB,
    mensagem TEXT,
    data DATE
);
'''

cursor.execute(create_table_query)

conn.commit()

conn.close()
