import os
from processar_pdf import *
from database import *

def indexar_arquivos(caminho_pasta):
    for nome_arquivo in os.listdir(caminho_pasta):
        if nome_arquivo.endswith(".pdf"):
            caminho_pdf = os.path.join(caminho_pasta, nome_arquivo)
            texto = processar_pdf(caminho_pdf)
            salvar_texto_pdf(nome_arquivo, texto)
