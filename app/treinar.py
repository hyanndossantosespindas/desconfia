# Pathlib permite trabalhar com caminhos de pastas e arquivos de forma segura
from pathlib import Path

# joblib salva e carrega o modelo treinado em um arquivo
import joblib
# pandas lê o arquivo CSV e organiza os dados em uma tabela (DataFrame)
import pandas as pd
# TfidfVectorizer transforma texto em números que o modelo consegue entender
from sklearn.feature_extraction.text import TfidfVectorizer
# LogisticRegression é o algoritmo que aprende a separar golpe de legítima
from sklearn.linear_model import LogisticRegression
# Estas funções medem o quanto o modelo acertou e errou
from sklearn.metrics import classification_report, confusion_matrix
# train_test_split divide os dados em um grupo para treinar e outro para testar
from sklearn.model_selection import train_test_split
# Pipeline junta vários passos (vetorizar + classificar) em um só objeto
from sklearn.pipeline import Pipeline
# StratifiedKFold divide os dados em partes mantendo a proporção de cada classe; cross_val_predict testa em cada parte
from sklearn.model_selection import StratifiedKFold, cross_val_predict

# Descobre a pasta raiz do projeto: este arquivo está em app/, então sobe dois níveis
RAIZ = Path(__file__).resolve().parent.parent
# Caminho do arquivo com as mensagens de exemplo
CSV = RAIZ / "data" / "mensagens.csv"
# Caminho onde o modelo treinado será salvo
MODELO = RAIZ / "models" / "modelo.joblib"


# Define a função principal, que executa todo o treino
def main():
    # Lê o CSV e guarda em uma tabela com as colunas "texto" e "rotulo"
    df = pd.read_csv(CSV)

    # Divide os dados em quatro partes: textos e rótulos de treino, textos e rótulos de teste
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        # Coluna com os textos das mensagens (entrada do modelo)
        df["texto"],
        # Coluna com as respostas certas: golpe ou legitima
        df["rotulo"],
        # 25% das mensagens ficam separadas para testar o modelo
        test_size=0.25,
        # Mantém a mesma proporção de golpe e legítima no treino e no teste
        stratify=df["rotulo"],
        # Fixa o sorteio, para o resultado ser igual a cada execução
        random_state=42,
    )

    # Monta o pipeline: os passos rodam em sequência, na ordem em que aparecem
    modelo = Pipeline([
        # Passo 1: converte texto em números, ignorando maiúsculas e acentos, e usando palavras soltas e pares de palavras
        ("tfidf", TfidfVectorizer(lowercase=True, strip_accents="unicode", ngram_range=(1, 2))),
        # Passo 2: o classificador; "balanced" evita que a classe com mais exemplos domine
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    # Treina o modelo usando só os dados de treino
    modelo.fit(x_treino, y_treino)

    # Pede ao modelo que preveja a classe das mensagens de teste, que ele nunca viu
    previsoes = modelo.predict(x_teste)
    # Mostra precisão, recall e F1 de cada classe; zero_division evita aviso se alguma métrica for zero
    print(classification_report(y_teste, previsoes, zero_division=0))
    # Explica como ler a tabela que vem a seguir
    print("Matriz de confusão (linhas = real, colunas = previsto; ordem: golpe, legitima)")
    # Mostra quantos acertos e erros houve em cada classe
    print(confusion_matrix(y_teste, previsoes, labels=["golpe", "legitima"]))

    # Cria uma validacao em 5 partes, embaralhando os dados com sorteio fixo
    validacao = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    # Para cada parte, treina com as outras quatro e preve esta; assim todas as mensagens são testadas
    previsoes_cv = cross_val_predict(modelo, df["texto"], df["rotulo"], cv=validacao)
    # Avisa que o relatorio a seguir usa todas as mensagens, e não só as 10 do teste 
    print("\nValidação cruzada (5 partes, todas as mensagens):")
    # Mostra precisão, recall e F1 de cada classe nessa avaliação mais ampla
    print(classification_report(df["rotulo"], previsoes_cv, zero_division=0))

    # Junta ao DataFrame uma coluna com o que o modelo previu para cada mensagem
    erros = df.assign(previsto=previsoes_cv)
    # Mantém só as linhas em que a resposta certa é diferente da previsão
    erros = erros[erros["rotulo"] != erros["previsto"]]
    # Avisa que a lista a seguir mostra os erros do modelo
    print("\nMensagens que o modelo errou:")
    # Percorre cada mensagem errada, uma por vez
    for _, linha in erros.iterrows():
        # Mostra a resposta real, a previsão e o texto da mensagem
        print(f"- real={linha['rotulo']} | previsto={linha['previsto']} | {linha['texto']}")
    
    # Cria a pasta models/ se ela ainda não existir
    MODELO.parent.mkdir(exist_ok=True)
    # Salva o modelo treinado no arquivo, para usar depois sem treinar de novo
    joblib.dump(modelo, MODELO)
    # Avisa onde o modelo foi salvo
    print(f"Modelo salvo em {MODELO}")


# Só executa main() quando o arquivo é rodado diretamente, e não quando é importado
if __name__ == "__main__":
    # Chama a função principal
    main()