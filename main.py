from dotenv import load_dotenv
import os
from indexador import indexar_arquivos
from processar_perguntas import processar_consulta, atualizar_contexto
from database import configurar_banco, obter_textos

# Definir a variável de ambiente para evitar o erro de duplicação do OpenMP
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Carregar variáveis de ambiente
load_dotenv()

# Configurar banco de dados
configurar_banco()

# Caminho para a pasta de PDFs
caminho_pasta = "data/"

# Indexar todos os PDFs na pasta
indexar_arquivos(caminho_pasta)

# Inicializar contexto
contexto_atual = ""

# Definir consultas e processá-las
consultas = [
    "quais são os dados de vida de um guerreiro?",
    "em quais situações eles são úteis e podem ajudar o grupo?",
    "quais são os dados de vida de um mago?"
]

for consulta in consultas:
    contexto_atual = atualizar_contexto(contexto_atual, consulta)
    textos = obter_textos()
    resposta = processar_consulta(consulta, textos, contexto_atual)
    print("Pergunta:", consulta)
    print("Resposta:", resposta)
    print("Contexto Atual:", contexto_atual)
    print("\n")
