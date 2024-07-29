import sqlite3
import json

def configurar_banco():
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cache (
        consulta TEXT PRIMARY KEY,
        resultado TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historico_conversas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pergunta TEXT,
        resposta TEXT
    )
    ''')
    conn.commit()
    conn.close()

def obter_historico_conversas(limite=15):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute("SELECT pergunta, resposta FROM historico_conversas ORDER BY id DESC LIMIT ?", (limite,))
    linhas = cursor.fetchall()
    conn.close()
    return [{"pergunta": linha[0], "resposta": linha[1]} for linha in linhas]

def salvar_entrada_historico(pergunta, resposta):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO historico_conversas (pergunta, resposta) VALUES (?, ?)", (pergunta, resposta))
    conn.commit()
    cursor.execute("DELETE FROM historico_conversas WHERE id NOT IN (SELECT id FROM historico_conversas ORDER BY id DESC LIMIT 15)")
    conn.commit()
    conn.close()
