import os
import json
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from models.Chat import PerguntaRequest, FeedbackRequest
from services.api_gemini import perguntar_ao_gemini
from config.database import SessionLocal
from models.Feedback import Feedback


caminho_arquivo = 'data/dados_site.json'


async def inicializar_dados_site():
    if not os.path.exists(caminho_arquivo) or await atualizar_scraping(caminho_arquivo):
        print('Extraindo dados do site...')
        print(f'Conteúdo atualizado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        await extrair_conteudo_site()
    return await carregar_conteudo_site()


async def atualizar_scraping(caminho):
    try:
        data_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho)).date()
        return data_modificacao < datetime.now().date()
    except Exception as error:
        print(f'⚠️ Erro ao verificar data do arquivo: {error}')
        return True


async def processar_pergunta(request: PerguntaRequest):
    pergunta_usuario = request.pergunta

    dados_site = await inicializar_dados_site()
    return await perguntar_ao_gemini(pergunta_usuario, dados_site)


async def extrair_conteudo_site():
    paginas = {
        'Página Principal': 'https://www.jovemprogramador.com.br',
        'Dúvidas Frequentes': 'https://www.jovemprogramador.com.br/duvidas.php',
        'Sobre o Programa': 'https://www.jovemprogramador.com.br/sobre.php',
        'Hackathon': 'https://www.jovemprogramador.com.br/hackathon/',
        'Inscrições PJP': 'https://www.jovemprogramador.com.br/inscricoes-jovem-programador/'
    }

    dados = []
    async with aiohttp.ClientSession() as session:
        for titulo, url in paginas.items():
            print(f'Extraindo conteúdo de: {titulo}')
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        print(f'❌ Erro ao acessar {url}')
                        continue
        
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    for tag_to_remove in soup(["script", "style", "noscript"]):
                        tag_to_remove.decompose()

                    bloco = {'titulo': titulo, 'conteudo': []}
                    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'ul', 'ol']):
                        if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
                            texto = tag.get_text(strip=True)
                            texto = " ".join(texto.split())
                            if texto:
                                bloco['conteudo'].append(texto)
                        elif tag.name in ['li', 'ul', 'ol']:
                            itens = []
                            for li in tag.find_all('li'):
                                li_texto = li.get_text(strip=True)
                                li_texto = " ".join(li_texto.split())
                                if li_texto:
                                    itens.append(li_texto)
                            if itens:
                                bloco['conteudo'].append({'tipo': 'lista', 'itens': itens})
                    
                    dados.append(bloco)
            except Exception as error:
                print(f'Erro ao processar {url}: \n{error}')

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print(f'✅ Conteúdo extraído e salvo em {caminho_arquivo}')


async def carregar_conteudo_site(caminho=caminho_arquivo):
    try:
        async with aiofiles.open(caminho, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        return 'Conteúdo do site não encontrado!'


async def getHealth():
    return { 'message': 'Api está online!' }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def registrar_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
   
    score = 1 if payload.score > 0 else -1

    feedback = Feedback(
        session_id=payload.session_id,
        score=score,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return {"status": "ok"}

