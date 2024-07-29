import sqlite3
import json

def obter_resultado_cache(consulta):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute("SELECT resultado FROM cache WHERE consulta = ?", (consulta,))
    linha = cursor.fetchone()
    conn.close()
    if linha:
        return json.loads(linha[0])
    return None

def salvar_resultado_cache(consulta, resultado):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO cache (consulta, resultado) VALUES (?, ?)", (consulta, json.dumps(resultado)))
    conn.commit()
    conn.close()
