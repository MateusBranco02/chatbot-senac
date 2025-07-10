import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv('API_KEY_GEMINI'))

model = genai.GenerativeModel('gemini-1.5-flash')


def perguntar_ao_gemini(pergunta, contexto):
    prompt = f"""
Responda a pergunta com base no conteúdo abaixo. Se a resposta não estiver presente nesse conteúdo, diga: 
"Desculpe, só posso responder perguntas relacionadas ao site jovemprogramador.com.br."

CONTEÚDO:
\"\"\"
{contexto}
\"\"\"

PERGUNTA:
{pergunta}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as error:
        return f'Erro ao acessar a IA: {str(error)}'
