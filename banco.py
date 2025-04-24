# banco.py
import sqlite3
import pandas as pd

DB_FILE = "pagamentos.db"

def conectar():
    return sqlite3.connect(DB_FILE)

def criar_tabela():
    conn = conectar()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano INTEGER,
            categoria TEXT,
            mes TEXT,
            valor REAL,
            pago INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def carregar_dados():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM pagamentos", conn)
    conn.close()
    return df

def salvar_pagamento(ano, categoria, mes, valor, pago):
    conn = conectar()
    conn.execute(
        "INSERT INTO pagamentos (ano, categoria, mes, valor, pago) VALUES (?, ?, ?, ?, ?)",
        (ano, categoria, mes, valor, int(pago))
    )
    conn.commit()
    conn.close()

def atualizar_status_pago(id_pagamento, pago):
    conn = conectar()
    conn.execute("UPDATE pagamentos SET pago = ? WHERE id = ?", (int(pago), id_pagamento))
    conn.commit()
    conn.close()

def remover_pagamento(id_pagamento):
    conn = conectar()
    conn.execute("DELETE FROM pagamentos WHERE id = ?", (id_pagamento,))
    conn.commit()
    conn.close()
