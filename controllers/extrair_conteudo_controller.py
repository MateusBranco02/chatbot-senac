import requests
from bs4 import BeautifulSoup


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
