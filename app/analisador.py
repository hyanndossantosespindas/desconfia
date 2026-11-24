# lru_cache guarda o resultado de uma função para não repetir o trabalho
from functools import lru_cache

# joblib carrega o modelo salvo no treino
import joblib

# Importa a função que gera a explicação com o Gemini
from app.explicador import explicar
# Importa o caminho onde o modelo treinado foi salvo
from app.treinar import MODELO


# Carrega o modelo só na primeira vez e reaproveita nas próximas chamadas
@lru_cache(maxsize=1)
def carregar_modelo():
    # Lê o arquivo do modelo; dá FileNotFoundError se ele ainda não foi treinado
    return joblib.load(MODELO)


# Recebe uma mensagem e devolve classificação, risco e explicação
def analisar(texto: str) -> dict:
    # Obtém o modelo treinado
    modelo = carregar_modelo()
    # Calcula a probabilidade de cada classe para a mensagem
    probabilidades = modelo.predict_proba([texto])[0]
    # Associa cada probabilidade ao nome da classe e pega a de "golpe"
    risco = float(dict(zip(modelo.classes_, probabilidades))["golpe"])
    # Devolve o resultado completo em um dicionário
    return {
        # Chance de golpe arredondada para duas casas decimais
        "risco": round(risco, 2),
        # Classe final: golpe se o risco for de 50% ou mais
        "classificacao": "golpe" if risco >= 0.5 else "legitima",
        # Texto explicativo gerado pelo Gemini
        "explicacao": explicar(texto, risco),
    }

