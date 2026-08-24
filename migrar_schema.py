import sqlite3

DB = "doacoes.db"
colunas_para_adicionar = {
    "nome": "TEXT",
    "cor": "TEXT",
    "tamanho": "TEXT",
    "observacoes": "TEXT",
    "data": "TEXT"
}

conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(doacoes)")
existing = [row[1] for row in cursor.fetchall()]
print("Colunas existentes:", existing)

for col, tipo in colunas_para_adicionar.items():
    if col not in existing:
        sql = f"ALTER TABLE doacoes ADD COLUMN {col} {tipo};"
        print("Executando:", sql)
        cursor.execute(sql)
    else:
        print(f"Coluna {col} já existe — pulando.")

conn.commit()
conn.close()
print("Migração concluída.")
