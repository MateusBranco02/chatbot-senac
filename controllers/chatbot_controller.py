import os
import json
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from datetime import datetime
from models.Chat import PerguntaRequest
from services.api_gemini import perguntar_ao_gemini


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


def filtrar_contexto(dados_site, pergunta: str, limite_caracteres: int = 6000) -> str:
    """Monta um contexto reduzido a partir do dados_site com base na pergunta.

    Estratégia simples:
    - extrai palavras-chave da pergunta (ignorando stopwords comuns);
    - percorre os blocos do site (título + conteúdos) e inclui trechos que
      contenham alguma dessas palavras;
    - concatena os trechos em uma única string até atingir um limite de tamanho.
    """

    if not dados_site:
        return ""

    pergunta_lower = (pergunta or "").lower()

    if "hackathon" in pergunta_lower:
        for bloco in dados_site:
            titulo = str(bloco.get("titulo", ""))
            if "hackathon" in titulo.lower():
                conteudos = bloco.get("conteudo", [])
                trechos = [f"[SEÇÃO: {titulo}]"]
                for item in conteudos:
                    if isinstance(item, dict) and item.get("tipo") == "lista":
                        texto_item = " | ".join(item.get("itens", []))
                    else:
                        texto_item = str(item)
                    trechos.append(texto_item)

                contexto_hackathon = "\n".join(trechos)

                return contexto_hackathon[:30000]

    stopwords = {"o", "a", "os", "as", "de", "da", "do", "das", "dos", "em", "no", "na", "nas", "nos",
                 "para", "por", "e", "ou", "um", "uma", "que", "com", "se", "sobre", "ao", "à", "às",
                 "dos", "das", "ser", "tem", "ter", "qual"}

    palavras = [p for p in pergunta_lower.replace("?", " ").replace(",", " ").split() if p and p not in stopwords]


    if not palavras:
        palavras = [p for p in pergunta_lower.split() if p]

    trechos_selecionados = []

    for bloco in dados_site:
        if len("\n".join(trechos_selecionados)) >= limite_caracteres:
            break

        titulo = str(bloco.get("titulo", ""))
        conteudos = bloco.get("conteudo", [])

        titulo_lower = titulo.lower()
        relevante_titulo = any(p in titulo_lower for p in palavras)

        if relevante_titulo:
            trechos_selecionados.append(f"[SEÇÃO: {titulo}]")

        for item in conteudos:
            if len("\n".join(trechos_selecionados)) >= limite_caracteres:
                break

            if isinstance(item, dict) and item.get("tipo") == "lista":
                texto_item = " | ".join(item.get("itens", []))
            else:
                texto_item = str(item)

            texto_lower = texto_item.lower()
            if relevante_titulo or any(p in texto_lower for p in palavras):
                trechos_selecionados.append(texto_item)

    if not trechos_selecionados:
        for bloco in dados_site:
            titulo = str(bloco.get("titulo", ""))
            conteudos = bloco.get("conteudo", [])
            trechos_selecionados.append(f"[SEÇÃO: {titulo}]")
            for item in conteudos[:5]:
                if isinstance(item, dict) and item.get("tipo") == "lista":
                    texto_item = " | ".join(item.get("itens", []))
                else:
                    texto_item = str(item)
                trechos_selecionados.append(texto_item)
                if len("\n".join(trechos_selecionados)) >= limite_caracteres:
                    break
            if len("\n".join(trechos_selecionados)) >= limite_caracteres:
                break

    contexto_reduzido = "\n".join(trechos_selecionados)
    return contexto_reduzido[:limite_caracteres]


async def processar_pergunta(request: PerguntaRequest):
    pergunta_usuario = request.pergunta

    dados_site = await inicializar_dados_site()
    contexto_reduzido = filtrar_contexto(dados_site, pergunta_usuario)
    return await perguntar_ao_gemini(pergunta_usuario, contexto_reduzido)


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

                    bloco = {'titulo': titulo, 'conteudo': []}
                    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'ul', 'ol']):
                        if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
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


async def carregar_conteudo_site(caminho=caminho_arquivo):
    try:
        async with aiofiles.open(caminho, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        return 'Conteúdo do site não encontrado!'


async def getHealth():
    return { 'message': 'Api está online!' }

