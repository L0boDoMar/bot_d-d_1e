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

def obter_historico_conversas():
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute("SELECT pergunta, resposta FROM historico_conversas ORDER BY id")
    linhas = cursor.fetchall()
    conn.close()
    return [{"pergunta": linha[0], "resposta": linha[1]} for linha in linhas]

def salvar_entrada_historico(pergunta, resposta):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO historico_conversas (pergunta, resposta) VALUES (?, ?)", (pergunta, resposta))
    conn.commit()
    conn.close()
