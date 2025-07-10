def carregar_conteudo_site(caminho='data/dados_site.txt'):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Conteúdo do site não encontrado!'