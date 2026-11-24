# os permite ler variáveis de ambiente, como os limites de uso
import os
# Path ajuda a achar a pasta de arquivos da página
from pathlib import Path

# FastAPI cria a API; HTTPException devolve erros HTTP; Request dá acesso a dados do visitante
from fastapi import FastAPI, HTTPException, Request
# FileResponse devolve um arquivo; StaticFiles serve CSS e JavaScript
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
# BaseModel e Field validam o formato dos dados que chegam e saem
from pydantic import BaseModel, Field

# Importa a função que classifica e explica a mensagem
from app.analisador import analisar
# Importa a classe que limita o uso
from app.limitador import LimitadorDeUso

# Cria a aplicação com título e descrição, que aparecem na página /docs
app = FastAPI(title="Desconfia", description="Detector de golpes em mensagens (projeto de estudo)")

# Caminho da pasta app/static, onde está a página
PASTA_ESTATICA = Path(__file__).resolve().parent / "static"
# Libera os arquivos da pasta no endereço /static
app.mount("/static", StaticFiles(directory=PASTA_ESTATICA), name="static")

# Limite por visitante: quantas análises por minuto (padrão 5, mudável pelo .env)
limite_por_visitante = LimitadorDeUso(maximo=int(os.getenv("LIMITE_POR_MINUTO", "5")), janela_segundos=60)
# Limite geral: quantas análises por hora no total, para proteger a cota do Gemini (padrão 100)
limite_geral = LimitadorDeUso(maximo=int(os.getenv("LIMITE_GERAL_POR_HORA", "100")), janela_segundos=3600)


# Página inicial: abre o index.html; include_in_schema=False a esconde do /docs
@app.get("/", include_in_schema=False)
def pagina_inicial():
    # Devolve o arquivo HTML da página
    return FileResponse(PASTA_ESTATICA / "index.html")


# Alguns navegadores pedem /favicon.ico automaticamente; devolvemos o mesmo ícone
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # Devolve o arquivo SVG com o tipo de mídia correto
    return FileResponse(PASTA_ESTATICA / "favicon.svg", media_type="image/svg+xml")


# Define o formato do pedido: um campo "texto" com entre 5 e 2000 caracteres
class Mensagem(BaseModel):
    # Se o texto for curto ou longo demais, a API recusa sozinha com erro 422
    texto: str = Field(min_length=5, max_length=2000)


# Define o formato da resposta
class Resultado(BaseModel):
    # Chance de golpe, de 0 a 1
    risco: float
    # "golpe" ou "legitima"
    classificacao: str
    # Explicação em linguagem simples
    explicacao: str


# Rota simples para checar se a API está no ar
@app.get("/saude")
def saude():
    # Devolve um status fixo
    return {"status": "ok"}

# Descobre o endereço do visitante; na Vercel o endereço real vem em cabeçalhos do proxy
def descobrir_visitante(requisicao: Request) -> str:
    # A Vercel define a variável VERCEL no ambiente; localmente ela não existe
    if os.getenv("VERCEL"):
        # O cabeçalho x-forwarded-for traz uma lista de endereços; o primeiro é o do visitante
        encaminhado = requisicao.headers.get("x-forwarded-for", "")
        # Se houver valor, devolve o primeiro endereço, sem espaços
        if encaminhado:
            return encaminhado.split(",")[0].strip()
    # Fora da Vercel, ou sem o cabeçalho, usa o endereço da conexão
    return requisicao.client.host if requisicao.client else "desconhecido"


# Rota principal: recebe uma mensagem (POST) e devolve a análise
@app.post("/analisar", response_model=Resultado)
def analisar_mensagem(mensagem: Mensagem, requisicao: Request):
    # Recusa textos formados só por espaços, que passam no tamanho mínimo
    if not mensagem.texto.strip():
        # Erro 422: dado inválido enviado pelo usuário
        raise HTTPException(status_code=422, detail="A mensagem não pode estar em branco.")

    # Identifica o visitante usando a função descobrir_visitante
    visitante = descobrir_visitante(requisicao)
    # Se este visitante já passou do limite por minuto, recusa
    if not limite_por_visitante.permitir(visitante):
        # Erro 429: muitas requisições; Retry-After diz quantos segundos esperar
        raise HTTPException(
            status_code=429,
            detail="Muitas verificações em pouco tempo. Aguarde um minuto e tente de novo.",
            headers={"Retry-After": "60"},
        )
    # Se o serviço todo já passou do limite por hora, recusa
    if not limite_geral.permitir("geral"):
        # Erro 429 com mensagem sobre o limite geral
        raise HTTPException(
            status_code=429,
            detail="O serviço atingiu o limite de uso por agora. Tente de novo mais tarde.",
            headers={"Retry-After": "3600"},
        )

    # Tenta analisar; se o modelo não existir, cai no bloco de erro
    try:
        # Devolve o resultado da análise
        return analisar(mensagem.texto)
    # Trata o caso de o modelo ainda não ter sido treinado
    except FileNotFoundError:
        # Erro 503: serviço ainda não está pronto, com instrução de como corrigir
        raise HTTPException(status_code=503, detail="Modelo não treinado. Rode: python -m app.treinar")