import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from services.api_gemini import perguntar_ao_gemini


caminho_arquivo = 'data/dados_site.json'


def inicializar_dados_site():
    if not os.path.exists(caminho_arquivo) or atualizar_scraping(caminho_arquivo, ):
        print('Extraindo dados do site...')
        print(f'Conteúdo atualizado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        extrair_conteudo_site()
    return carregar_conteudo_site()


def atualizar_scraping(caminho):
    try:
        data_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho)).date()
        return data_modificacao < datetime.now().date()
    except Exception as error:
        print(f'⚠️ Erro ao verificar data do arquivo: {error}')
        return True


def processar_pergunta(pergunta):
    dados_site = inicializar_dados_site()
    return perguntar_ao_gemini(pergunta, dados_site)


def extrair_conteudo_site():
    paginas = {
        'Página Principal': 'https://www.jovemprogramador.com.br',
        'Dúvidas Frequentes': 'https://www.jovemprogramador.com.br/duvidas.php',
        'Sobre o Programa': 'https://www.jovemprogramador.com.br/sobre.php',
        'Hackathon': 'https://www.jovemprogramador.com.br/hackathon/'
    }

    dados = []

    for titulo, url in paginas.items():
        print(f'Extraindo conteúdo de: {titulo}')
        try:
            response = requests.get(url)

            if response.status_code != 200:
                # raise Exception('Erro ao acessar o site!')
                print(f'❌ Erro ao acessar {url}')
                continue
    
            soup = BeautifulSoup(response.text, "html.parser")

            bloco = {'titulo': titulo, 'conteudo': []}
            for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'ul', 'ol']):
                if tag.name in ['h1', 'h2', 'h3', 'p']:
                    texto = tag.get_text(strip=True)
                    if texto:
                        bloco['conteudo'].append(texto)
                elif tag.name in ['li', 'ul', 'ol']:
                    itens = [li.get_text(strip=True) for li in tag.find_all('li') if li.get_text(strip=True)]
                    if itens:
                        bloco['conteudo'].append({'tipo': 'lista', 'itens': itens})
            
            dados.append(bloco)
        except Exception as error:
            print(f'Erro ao processar {url}: \n{error}')

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print(f'✅ Conteúdo extraído e salvo em {caminho_arquivo}')


def carregar_conteudo_site(caminho=caminho_arquivo):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return 'Conteúdo do site não encontrado!'

