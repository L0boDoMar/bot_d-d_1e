import fitz  # PyMuPDF
import os

def processar_pdf(caminho_pdf):
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(f"O arquivo PDF {caminho_pdf} não foi encontrado.")

    # Extrair texto do PDF usando PyMuPDF
    doc = fitz.open(caminho_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()

    # Verifica se o texto foi lido corretamente
    if not texto:
        raise ValueError("O texto lido do arquivo está vazio.")
    
    return texto
