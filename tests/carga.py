import asyncio
import time
import aiohttp
import random
import json
from pathlib import Path

BASE_URL = "https://synna.onrender.com"

PERGUNTAS = [
    "Qual o objetivo do programa Jovem Programador?",
    "Quais são os requisitos para participar?",
    "Quanto tempo dura o curso?",
    "O curso é gratuito?",
    "Onde são as aulas?",
    "Qual a idade mínima para participar?",
    "Precisa ter conhecimento prévio?",
    "Como funciona o processo seletivo?",
    "Quais linguagens de programação são ensinadas?",
    "Tem certificado no final do curso?",
    "Qual o horário das aulas?",
    "Posso fazer outros cursos junto?",
    "Tem aulas práticas?",
    "Quais são os parceiros do programa?",
    "Como funciona o hackathon?",
]


async def executar_carga(num_requests: int = 10):
    inicio_teste = time.time()

    resultados = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            pergunta = random.choice(PERGUNTAS)
            tasks.append(executar_requisicao(session, pergunta, i + 1))

        respostas = await asyncio.gather(*tasks)
        resultados.extend(respostas)

    fim_teste = time.time()

    tempos = [r["tempo_resposta"] for r in resultados]
    status_codes = [r["status_code"] for r in resultados]

    total = len(resultados)
    sucessos = sum(1 for s in status_codes if s == 200)
    erros = total - sucessos

    resumo = {
        "total_requisicoes": total,
        "sucessos": sucessos,
        "erros": erros,
        "tempo_total_segundos": round(fim_teste - inicio_teste, 2),
        "tempo_medio_segundos": round(sum(tempos) / total, 2) if total > 0 else 0,
        "tempo_min_segundos": round(min(tempos), 2) if tempos else 0,
        "tempo_max_segundos": round(max(tempos), 2) if tempos else 0,
    }

    salvar_relatorio(resumo, resultados)
    exibir_resumo_console(resumo)


async def executar_requisicao(session: aiohttp.ClientSession, pergunta: str, indice: int):
    inicio = time.time()
    try:
        async with session.post(f"{BASE_URL}/api/pergunta", json={"pergunta": pergunta}) as resp:
            status = resp.status
            try:
                corpo = await resp.json()
            except Exception:
                corpo = await resp.text()
    except Exception as e:
        status = 0
        corpo = str(e)
    fim = time.time()

    return {
        "indice": indice,
        "pergunta": pergunta,
        "status_code": status,
        "tempo_resposta": round(fim - inicio, 2),
        "resposta_resumida": (str(corpo)[:200] + "...") if len(str(corpo)) > 200 else str(corpo),
    }


def salvar_relatorio(resumo: dict, detalhes: list):
    pasta_reports = Path("tests/reports")
    pasta_reports.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    arquivo = pasta_reports / f"load_test_{timestamp}.json"

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump({"resumo": resumo, "detalhes": detalhes}, f, ensure_ascii=False, indent=2)

    print(f"\n📁 Relatório salvo em: {arquivo}")


def exibir_resumo_console(resumo: dict):
    print("\n===== RELATÓRIO DO TESTE DE CARGA =====")
    print(f"Total de requisições: {resumo['total_requisicoes']}")
    print(f"Sucessos (status 200): {resumo['sucessos']}")
    print(f"Erros: {resumo['erros']}")
    print(f"Tempo total: {resumo['tempo_total_segundos']}s")
    print(f"Tempo médio: {resumo['tempo_medio_segundos']}s")
    print(f"Tempo mínimo: {resumo['tempo_min_segundos']}s")
    print(f"Tempo máximo: {resumo['tempo_max_segundos']}s")
    print("======================================\n")


if __name__ == "__main__":
    # Ajuste aqui o número de requisições para o teste de apresentação
    NUM_REQUESTS = 10
    asyncio.run(executar_carga(NUM_REQUESTS))
