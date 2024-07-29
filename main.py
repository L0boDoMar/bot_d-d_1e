from dotenv import load_dotenv
import os
from processar_pdf import *
from processar_perguntas import *
from database import *

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

# Inicializar contexto
contexto_atual = ""

# Definir consultas e processá-las
consultas = [
    "qual é o atributo principal do mago?",
    "quantos feitiços eles podem memorizar no inicio?",
    "qual é oa atributo principal dos guerreiros?"
]

for consulta in consultas:
    contexto_atual = atualizar_contexto(contexto_atual, consulta)
    resposta = processar_consulta(consulta, texto, contexto_atual)
    print("Pergunta:", consulta)
    print("Resposta:", resposta)
   # print("Contexto Atual:", contexto_atual)
