# TestClient simula chamadas à API sem precisar subir o servidor
from fastapi.testclient import TestClient

# Importa a aplicação que vamos testar
from app.main import app

# No topo do arquivo, junto dos outros imports:
from app.limitador import LimitadorDeUso

# Cria o cliente de teste ligado à aplicação
cliente = TestClient(app)


# Substitui a análise real por uma resposta fixa, para não chamar o Gemini
def analise_falsa(texto):
    # Devolve um resultado fixo com o mesmo formato da resposta real
    return {"risco": 0.9, "classificacao": "golpe", "explicacao": "explicação de teste"}


# Testa a rota de saúde
def test_saude():
    # Faz uma chamada GET para /saude
    resposta = cliente.get("/saude")
    # Confere que o código é 200 (sucesso)
    assert resposta.status_code == 200
    # Confere que o corpo da resposta é o esperado
    assert resposta.json() == {"status": "ok"}


# Testa uma análise com sucesso; monkeypatch troca a função real pela falsa
def test_analisar_mensagem_valida(monkeypatch):
    # Troca a função analisar usada pela API pela versão falsa
    monkeypatch.setattr("app.main.analisar", analise_falsa)
    # Envia uma mensagem de teste
    resposta = cliente.post("/analisar", json={"texto": "Sua conta foi bloqueada, acesse o link agora."})
    # Confere o código de sucesso
    assert resposta.status_code == 200
    # Confere que a classificação veio como esperado
    assert resposta.json()["classificacao"] == "golpe"


# Testa a recusa de um texto curto demais
def test_texto_curto_demais():
    # Envia um texto de 2 letras, abaixo do mínimo de 5
    resposta = cliente.post("/analisar", json={"texto": "oi"})
    # Confere que a API recusou com erro 422
    assert resposta.status_code == 422


# Testa a recusa de um texto formado só por espaços
def test_texto_em_branco():
    # Envia 10 espaços, que passam no tamanho mínimo mas não têm conteúdo
    resposta = cliente.post("/analisar", json={"texto": "          "})
    # Confere que a API recusou com erro 422
    assert resposta.status_code == 422


# Testa o erro quando o modelo ainda não foi treinado
def test_modelo_nao_treinado(monkeypatch):
    # Cria uma função que simula a ausência do arquivo do modelo
    def sem_modelo(texto):
        # Levanta o mesmo erro que aconteceria sem o modelo treinado
        raise FileNotFoundError()
    # Troca a função analisar por essa versão que falha
    monkeypatch.setattr("app.main.analisar", sem_modelo)
    # Envia uma mensagem válida
    resposta = cliente.post("/analisar", json={"texto": "Sua conta foi bloqueada, acesse o link agora."})
    # Confere que a API respondeu 503 (serviço não pronto)
    assert resposta.status_code == 503

# Testa que a API devolve 429 quando o visitante passa do limite
def test_limite_de_uso_devolve_429(monkeypatch):
    # Troca o limitador por um que não permite nenhum uso
    monkeypatch.setattr("app.main.limite_por_visitante", LimitadorDeUso(maximo=0, janela_segundos=60))
    # Envia uma mensagem válida
    resposta = cliente.post("/analisar", json={"texto": "Sua conta foi bloqueada, acesse o link agora."})
    # Confere que a API respondeu 429 (muitas requisições)
    assert resposta.status_code == 429    