# Importa a classe que vamos testar
from app.limitador import LimitadorDeUso


# Testa que o limitador permite até o máximo e depois recusa
def test_permite_ate_o_maximo_e_depois_recusa():
    # Cria um limitador de 2 usos por minuto
    limitador = LimitadorDeUso(maximo=2, janela_segundos=60)
    # Os dois primeiros usos são permitidos
    assert limitador.permitir("visitante-a") is True
    assert limitador.permitir("visitante-a") is True
    # O terceiro é recusado
    assert limitador.permitir("visitante-a") is False


# Testa que cada visitante tem o seu próprio limite
def test_visitantes_diferentes_nao_se_afetam():
    # Cria um limitador de 1 uso por minuto
    limitador = LimitadorDeUso(maximo=1, janela_segundos=60)
    # O visitante A usa a sua vez
    assert limitador.permitir("visitante-a") is True
    # O visitante A é bloqueado
    assert limitador.permitir("visitante-a") is False
    # O visitante B ainda pode usar
    assert limitador.permitir("visitante-b") is True