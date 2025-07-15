import os
import requests
from bs4 import BeautifulSoup
from services.api_gemini import perguntar_ao_gemini


caminho_arquivo = 'data/dados_site.txt'


def inicializar_dados_site():
    if not os.path.exists(caminho_arquivo):
        extrair_conteudo_site()
    return carregar_conteudo_site()


def processar_pergunta(pergunta):
    dados_site = inicializar_dados_site()
    return perguntar_ao_gemini(pergunta, dados_site)


def extrair_conteudo_site():
    url = 'https://www.jovemprogramador.com.br'
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('Erro ao acessar o site!')
    
    soup = BeautifulSoup(response.text, "html.parser")

    textos = []

    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']):
        texto = tag.get_text(strip=True)
        if texto:
            textos.append(texto)
    
    conteudo_extraido = '\n'.join(textos)

    with open("data/dados_site.txt", "w", encoding="utf-8") as f:
        f.write(conteudo_extraido)
    
    print('✅ Conteúdo extraído e salvo em data/dados_site.txt')


def carregar_conteudo_site(caminho='data/dados_site.txt'):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Conteúdo do site não encontrado!'

