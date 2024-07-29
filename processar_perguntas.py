import time
from transformers import GPT2TokenizerFast
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from database import *
from cache import *
import os
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def calcular_similaridade(texto1, texto2):
    vectorizer = TfidfVectorizer().fit_transform([texto1, texto2])
    vectors = vectorizer.toarray()
    cos_sim = cosine_similarity(vectors)
    return cos_sim[0, 1]

def atualizar_contexto(contexto_atual, nova_consulta, limiar_similaridade=0.2):
    if not contexto_atual:
        return nova_consulta

    similaridade = calcular_similaridade(contexto_atual, nova_consulta)
    if similaridade < limiar_similaridade:
        return nova_consulta
    return contexto_atual

def processar_consulta(consulta, texto, contexto_atual):
    # Inicializar o tokenizador
    tokenizador = GPT2TokenizerFast.from_pretrained("gpt2")

    # Função para contar tokens
    def contar_tokens(texto: str) -> int:
        return len(tokenizador.encode(texto))

    # Dividir o texto em chunks
    divisor_texto = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=24,
        length_function=contar_tokens,
    )

    chunks = divisor_texto.create_documents([texto])

    if not chunks:
        raise ValueError("Os chunks de texto não foram criados corretamente.")
    
    # Criar embeddings
    chave_api_openai = os.getenv("OPENAI_API_KEY")
    embeddings = OpenAIEmbeddings(openai_api_key=chave_api_openai, model="text-embedding-3-small")

    # Verificar se os embeddings estão sendo gerados corretamente
    texto_chunks = [pedaço.page_content for pedaço in chunks]
    lista_embeddings = embeddings.embed_documents(texto_chunks)
    if not lista_embeddings:
        raise ValueError("Os embeddings não foram gerados corretamente.")
    if len(lista_embeddings) == 0:
        raise ValueError("A lista de embeddings está vazia.")
    
    # Criar o banco de dados FAISS
    db = FAISS.from_documents(chunks, embeddings)

    # Função para verificar e usar o cache, mantendo o contexto da conversa
    def consulta_cache(consulta, documentos_entrada, historico, novo_contexto):
        start_time = time.time()
        resultado_cache = obter_resultado_cache(consulta)
        if resultado_cache and not novo_contexto:
            print("Resposta recuperada do cache.")
            print("Tempo de resposta (cache):", time.time() - start_time, "segundos")
            return resultado_cache['output_text']
        else:
            print("Resposta obtida da API.")
            contexto_completo = "\n".join([f"Q: {entrada['pergunta']}\nA: {entrada['resposta']}" for entrada in historico])
            if contexto_completo:
                contexto_completo += "\n"
            contexto_completo += f"Q: {consulta}"
            llm = ChatOpenAI(openai_api_key=chave_api_openai, temperature=0, max_tokens=50)
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
    
    # Obter histórico de conversas limitado
    historico = obter_historico_conversas()

    # Verificar similaridade com histórico
    novo_contexto = True
    if contexto_atual:
        novo_contexto = False

    # Executar a cadeia com a consulta
    return consulta_cache(consulta, docs, historico if not novo_contexto else [], novo_contexto)
