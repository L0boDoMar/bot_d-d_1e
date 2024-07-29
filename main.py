from dotenv import load_dotenv
import os
from processar_pdf import processar_pdf
from processar_perguntas import processar_consulta
from database import configurar_banco

# Definir a variável de ambiente para evitar o erro de duplicação do OpenMP
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Carregar variáveis de ambiente
load_dotenv()

# Configurar banco de dados
configurar_banco()

# Caminho para o PDF
caminho_pdf = "data/dungeons_and_dragons.pdf"

# Processar o PDF e extrair o texto
texto = processar_pdf(caminho_pdf)

# Definir a consulta e processá-la
consulta = "em quais situações o guerreiro é útil?"
resposta = processar_consulta(consulta, texto)

print("Pergunta:", consulta)
print("Resposta:", resposta)
