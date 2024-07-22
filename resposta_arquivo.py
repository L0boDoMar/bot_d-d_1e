from dotenv import load_dotenv
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from transformers import GPT2TokenizerFast
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
import fitz  # PyMuPDF

# Carregar variáveis de ambiente
load_dotenv()

# Obter chave da API OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não está definida.")

# Processar o PDF e extrair o texto diretamente na memória
pdf_path = "data/dungeons_and_dragons.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"O arquivo PDF {pdf_path} não foi encontrado.")

# Extrair texto do PDF usando PyMuPDF
doc = fitz.open(pdf_path)
text = ""
for page in doc:
    text += page.get_text()

# Verifica se o texto foi lido corretamente
if not text:
    raise ValueError("O texto lido do arquivo está vazio.")
#print("Texto lido do PDF:", text[:500])  # Opcional: Exibir os primeiros 500 caracteres do texto

# Inicializar o tokenizador
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

# Função para contar tokens
def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

# Dividir o texto em pedaços
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=24,
    length_function=count_tokens,
)

chunks = text_splitter.create_documents([text])

if not chunks:
    raise ValueError("Os chunks de texto não foram criados corretamente.")
#print("Primeiros 5 chunks:", [chunk.page_content for chunk in chunks[:5]])  # Opcional: Exibir os primeiros 5 chunks

# Criar embeddings
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-ada-002")

# Verificar se os embeddings estão sendo gerados corretamente
chunk_texts = [chunk.page_content for chunk in chunks]
embeddings_list = embeddings.embed_documents(chunk_texts)
if not embeddings_list:
    raise ValueError("Os embeddings não foram gerados corretamente.")
if len(embeddings_list) == 0:
    raise ValueError("A lista de embeddings está vazia.")
#print("Primeiros 5 embeddings:", embeddings_list[:5])  # Opcional: Exibir os primeiros 5 embeddings

# Criar o banco de dados FAISS
db = FAISS.from_documents(chunks, embeddings)

# Definir a consulta e realizar a busca por similaridade
query = "quais são os dados de vida de um guerreiro?"
docs = db.similarity_search(query)
if not docs:
    raise ValueError("Nenhum documento semelhante encontrado para a consulta.")
#print("Primeiro documento retornado:", docs[0])

# Inicializar a cadeia de perguntas e respostas
chain = load_qa_chain(OpenAI(openai_api_key=openai_api_key, temperature=0, max_tokens=50), chain_type="stuff")

# Executar a cadeia com a consulta
answer = chain.invoke({"input_documents": docs, "question": query})
print("Resposta:", answer)
