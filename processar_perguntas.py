import time
from transformers import GPT2TokenizerFast
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
from database import *
from cache import *
import os
import json

def processar_consulta(consulta, texto):
    # Inicializar o tokenizador
    tokenizador = GPT2TokenizerFast.from_pretrained("gpt2")

    # Função para contar tokens
    def contar_tokens(texto: str) -> int:
        return len(tokenizador.encode(texto))

    # Dividir o texto em pedaços
    divisor_texto = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=24,
        length_function=contar_tokens,
    )

    pedaços = divisor_texto.create_documents([texto])

    if not pedaços:
        raise ValueError("Os pedaços de texto não foram criados corretamente.")
    
    # Criar embeddings
    chave_api_openai = os.getenv("OPENAI_API_KEY")
    embeddings = OpenAIEmbeddings(openai_api_key=chave_api_openai, model="text-embedding-3-small")

    # Verificar se os embeddings estão sendo gerados corretamente
    texto_pedaços = [pedaço.page_content for pedaço in pedaços]
    lista_embeddings = embeddings.embed_documents(texto_pedaços)
    if not lista_embeddings:
        raise ValueError("Os embeddings não foram gerados corretamente.")
    if len(lista_embeddings) == 0:
        raise ValueError("A lista de embeddings está vazia.")
    
    # Criar o banco de dados FAISS
    db = FAISS.from_documents(pedaços, embeddings)

    # Função para verificar e usar o cache, mantendo o contexto da conversa
    def consulta_cache(consulta, documentos_entrada):
        start_time = time.time()
        historico = obter_historico_conversas()
        resultado_cache = obter_resultado_cache(consulta)
        if resultado_cache:
            print("Resposta recuperada do cache.")
            print("Tempo de resposta (cache):", time.time() - start_time, "segundos")
            return resultado_cache['output_text']
        else:
            print("Resposta obtida da API.")
            contexto_completo = "\n".join([f"Q: {entrada['pergunta']}\nA: {entrada['resposta']}" for entrada in historico])
            if contexto_completo:
                contexto_completo += "\n"
            contexto_completo += f"Q: {consulta}"
            llm = OpenAI(openai_api_key=chave_api_openai, temperature=0, max_tokens=150)
            chain = load_qa_chain(llm, chain_type="stuff")
            resultado = chain.invoke({"input_documents": documentos_entrada, "question": contexto_completo})
            
            # Extrair a resposta do dicionário e salvar como string
            resposta_str = resultado['output_text']
            
            salvar_entrada_historico(consulta, resposta_str)
            salvar_resultado_cache(consulta, {
                'input_documents': [doc.page_content for doc in documentos_entrada], 
                'question': consulta, 
                'output_text': resposta_str
            })
            print("Tempo de resposta (API):", time.time() - start_time, "segundos")
            return resposta_str

    # Realizar a busca por similaridade
    docs = db.similarity_search(consulta)
    if not docs:
        raise ValueError("Nenhum documento semelhante encontrado para a consulta.")
    
    # Executar a cadeia com a consulta
    return consulta_cache(consulta, docs)
