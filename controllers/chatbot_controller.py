import os
from models.scraping_site import carregar_conteudo_site
from services.api_gemini import perguntar_ao_gemini
from controllers.extrair_conteudo_controller import extrair_conteudo_site

caminho_arquivo = 'data/dados_site.txt'

if not os.path.exists(caminho_arquivo):
    extrair_conteudo_site()

dados_site = carregar_conteudo_site()


def processar_pergunta(pergunta):
    return perguntar_ao_gemini(pergunta, dados_site)
