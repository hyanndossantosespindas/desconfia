# deque é uma fila eficiente; defaultdict cria uma fila nova para cada visitante
from collections import defaultdict, deque
# monotonic é um relógio que nunca volta atrás, bom para medir intervalos
from time import monotonic
# Lock evita que duas requisições mexam nos registros ao mesmo tempo
from threading import Lock


# Limita quantas vezes cada chave (por exemplo, um visitante) pode agir em um período
class LimitadorDeUso:
    # Recebe o máximo de usos permitidos e o tamanho da janela em segundos
    def __init__(self, maximo: int, janela_segundos: int):
        # Guarda o máximo permitido por janela
        self.maximo = maximo
        # Guarda o tamanho da janela de tempo
        self.janela = janela_segundos
        # Guarda, para cada chave, os momentos dos usos recentes
        self.registros = defaultdict(deque)
        # Cria a trava de segurança para uso simultâneo
        self.trava = Lock()

    # Devolve True se a chave ainda pode usar, e registra o uso; False se passou do limite
    def permitir(self, chave: str) -> bool:
        # Anota o horário atual
        agora = monotonic()
        # Garante que só uma requisição por vez altere os registros
        with self.trava:
            # Pega a fila de usos desta chave
            fila = self.registros[chave]
            # Remove os usos antigos, que já saíram da janela de tempo
            while fila and agora - fila[0] > self.janela:
                # Tira o uso mais antigo da fila
                fila.popleft()
            # Se já atingiu o máximo, recusa
            if len(fila) >= self.maximo:
                # Avisa que o limite foi atingido
                return False
            # Registra este uso
            fila.append(agora)
            # Autoriza
            return True