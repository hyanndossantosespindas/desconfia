# FastAPI cria a API; HTTPException devolve erros HTTP com mensagem clara
from fastapi import FastAPI, HTTPException
# BaseModel e Field validam o formato dos dados que chegam e saem
from pydantic import BaseModel, Field

# Importa a função que classifica e explica a mensagem
from app.analisador import analisar

# Cria a aplicação com título e descrição, que aparecem na página /docs
app = FastAPI(title="Desconfia", description="Detector de golpes em mensagens (projeto de estudo)")


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

# Rota principal: recebe uma mensagem (POST) e devolve a análise
@app.post("/analisar", response_model=Resultado)
def analisar_mensagem(mensagem: Mensagem):
    # Recusa textos formados só por espaços, que passam no tamanho mínimo
    if not mensagem.texto.strip():
        # Erro 422: dado inválido enviado pelo usuário
        raise HTTPException(status_code=422, detail="A mensagem não pode estar em branco.")
    # Tenta analisar; se o modelo não existir, cai no bloco de erro
    try:
        # Devolve o resultado da análise
        return analisar(mensagem.texto)
    # Trata o caso de o modelo ainda não ter sido treinado
    except FileNotFoundError:
        # Erro 503: serviço ainda não está pronto, com instrução de como corrigir
        raise HTTPException(status_code=503, detail="Modelo não treinado. Rode: python -m app.treinar")    