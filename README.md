# Desconfia

Detector de golpes em mensagens (SMS, WhatsApp, e-mail). Você envia um texto suspeito, e a API devolve o risco de golpe, a classificação e uma explicação em linguagem simples dos sinais de alerta.

> Projeto de estudo. Todos os dados são fictícios e o modelo é pequeno. Não use como única fonte de decisão.

## Como funciona

1. **Classificador** (scikit-learn): TF-IDF + regressão logística, treinado em uma base de mensagens fictícias de golpe e legítimas.
2. **Explicação** (Gemini): a partir do texto e do risco calculado, gera uma explicação curta, apontando sinais como urgência, link suspeito e pedido de código.
3. **API** (FastAPI): recebe a mensagem, valida a entrada e devolve o resultado.

## Resultados

Validação cruzada em 5 partes, sobre 64 mensagens fictícias (32 golpes e 32 legítimas):

| Classe | Precisão | Recall | F1 |
|---|---|---|---|
| golpe | 0,82 | 0,84 | 0,83 |
| legítima | 0,84 | 0,81 | 0,83 |

Acurácia geral: 0,83.

## Limitações

- A base tem só 64 mensagens inventadas, sem variedade real. O resultado acima **não** representa o desempenho com mensagens reais.
- Mesmo em golpes óbvios, a confiança do modelo pode ser baixa (por exemplo, 62%).
- A explicação do Gemini pode soar mais forte do que o número do classificador.
- O texto analisado é enviado à API do Google, então use apenas mensagens fictícias.

## Como rodar

```bash
git clone https://github.com/hyanndossantosespindas/desconfia.git
cd desconfia
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash). No PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz, com base no `.env.example`:

```
GEMINI_API_KEY=sua_chave
GEMINI_MODEL=gemini-3.1-flash-lite
```

Treine o modelo e suba a API:

```bash
python -m app.treinar
python -m uvicorn app.api:app --reload
```

Abra `http://127.0.0.1:8000/docs` para testar.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/saude` | Verifica se a API está no ar |
| POST | `/analisar` | Recebe `{"texto": "..."}` e devolve `risco`, `classificacao` e `explicacao` |

Erros tratados: texto muito curto ou em branco (422), modelo não treinado (503) e falha na geração da explicação (a API responde com aviso, sem quebrar).

## Testes

```bash
python -m pytest -v
```

Os testes não chamam o Gemini.

## Stack

Python, scikit-learn, pandas, FastAPI, pytest, Google Gemini API.