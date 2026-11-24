// Pega o campo onde a pessoa cola a mensagem
const campoTexto = document.getElementById("texto");
// Pega o texto que mostra quantas letras já foram digitadas
const contagem = document.getElementById("contagem");
// Pega o botão que inicia a verificação
const botaoVerificar = document.getElementById("verificar");
// Pega o botão que limpa tudo
const botaoLimpar = document.getElementById("limpar");
// Pega o botão que preenche uma mensagem de exemplo
const botaoExemplo = document.getElementById("exemplo");
// Pega o parágrafo onde aparecem os erros
const areaErro = document.getElementById("erro");
// Pega o cartão onde aparece o resultado
const areaResultado = document.getElementById("resultado");
// Pega o título do resultado
const tituloResultado = document.getElementById("titulo-resultado");
// Pega o parágrafo da explicação
const textoExplicacao = document.getElementById("explicacao");
// Pega o parágrafo que mostra a confiança do sistema
const textoConfianca = document.getElementById("confianca");
// Pega a lista de passos recomendados
const listaPassos = document.getElementById("passos");
// Pega a barra do medidor visual de risco
const barra = document.getElementById("barra");

// Mensagem fictícia usada no botão de exemplo
const MENSAGEM_EXEMPLO =
  "URGENTE: sua conta foi bloqueada. Acesse banco-seguro.exemplo.com para desbloquear em 1 hora.";

// Orientações para cada nível de risco
const PASSOS = {
  // Passos para quando o risco é alto
  alto: [
    "Não clique em nenhum link da mensagem.",
    "Não envie códigos, senhas nem dinheiro.",
    "Ligue para o número oficial da empresa, que está no site ou no cartão.",
    "Apague a mensagem e, se puder, bloqueie o número.",
  ],
  // Passos para quando o risco é médio
  medio: [
    "Não clique em links antes de confirmar.",
    "Procure a empresa pelo aplicativo ou telefone oficial.",
    "Desconfie de pressa e de pedidos de código ou dinheiro.",
  ],
  // Passos para quando o risco é baixo
  baixo: [
    "Mesmo assim, evite clicar em links que você não esperava.",
    "Na dúvida, confirme pelo canal oficial da empresa.",
  ],
};

// Esconde o erro e o resultado antes de uma nova verificação
function limparMensagens() {
  // Esconde a área de erro
  areaErro.hidden = true;
  // Esconde a área de resultado
  areaResultado.hidden = true;
}

// Mostra uma mensagem de erro para a pessoa
function mostrarErro(mensagem) {
  // Escreve o texto do erro; textContent evita inserir código por engano
  areaErro.textContent = mensagem;
  // Torna a área de erro visível
  areaErro.hidden = false;
}

// Mostra o resultado da análise
function mostrarResultado(dados) {
  // Escolhe o nível conforme o risco: 70% ou mais é alto, 50% a 69% é médio, abaixo disso é baixo
  const nivel = dados.risco >= 0.7 ? "alto" : dados.risco >= 0.5 ? "medio" : "baixo";
  // Define o título de cada nível
  const titulos = {
    alto: "⚠️ Muito provável que seja golpe",
    medio: "⚠️ Pode ser golpe. Tenha cuidado",
    baixo: "✅ Parece segura, mas confira",
  };
  // Troca a cor do cartão conforme o nível
  areaResultado.className = "cartao resultado " + nivel;
  // Escreve o título do resultado
  tituloResultado.textContent = titulos[nivel];
  // Escreve a explicação devolvida pela API
  textoExplicacao.textContent = dados.explicacao;
  // Mostra a chance de golpe em porcentagem
  textoConfianca.textContent =
    "O sistema estima " + Math.round(dados.risco * 100) + "% de chance de ser golpe.";
  // Enche a barra do medidor de acordo com a chance de golpe
  barra.style.width = Math.round(dados.risco * 100) + "%";
  // Esvazia a lista de passos anterior
  listaPassos.innerHTML = "";
  // Percorre os passos do nível escolhido
  PASSOS[nivel].forEach((passo) => {
    // Cria um item de lista
    const item = document.createElement("li");
    // Escreve o passo dentro do item
    item.textContent = passo;
    // Coloca o item na lista
    listaPassos.appendChild(item);
  });
  // Torna o cartão de resultado visível
  areaResultado.hidden = false;
  // Leva a tela até o resultado e move o foco para ele
  areaResultado.scrollIntoView({ behavior: "smooth", block: "start" });
  areaResultado.focus();
}

// Atualiza o contador de letras quando a pessoa digita
campoTexto.addEventListener("input", () => {
  // Mostra o tamanho atual do texto
  contagem.textContent = campoTexto.value.length;
});

// Limpa o campo e as mensagens quando clica em "Limpar"
botaoLimpar.addEventListener("click", () => {
  // Esvazia o campo de texto
  campoTexto.value = "";
  // Zera o contador
  contagem.textContent = "0";
  // Esconde erro e resultado
  limparMensagens();
  // Devolve o foco ao campo de texto
  campoTexto.focus();
});

// Preenche o campo com o exemplo quando clica no link
botaoExemplo.addEventListener("click", () => {
  // Coloca a mensagem de exemplo no campo
  campoTexto.value = MENSAGEM_EXEMPLO;
  // Atualiza o contador de letras
  contagem.textContent = String(MENSAGEM_EXEMPLO.length);
  // Esconde erro e resultado antigos
  limparMensagens();
});

// Faz a verificação quando clica em "Verificar mensagem"
botaoVerificar.addEventListener("click", async () => {
  // Esconde mensagens antigas
  limparMensagens();
  // Lê o texto e tira espaços das pontas
  const texto = campoTexto.value.trim();
  // Se o texto for muito curto, avisa antes de chamar a API
  if (texto.length < 5) {
    // Mostra um erro em linguagem simples
    mostrarErro("Escreva ou cole uma mensagem com pelo menos 5 letras.");
    // Para aqui, sem chamar a API
    return;
  }
  // Desativa o botão para evitar cliques repetidos
  botaoVerificar.disabled = true;
  // Mostra que está trabalhando
  botaoVerificar.textContent = "Verificando...";
  // Tenta chamar a API; falhas de rede caem no catch
  try {
    // Envia a mensagem para a API
    const resposta = await fetch("/analisar", {
      // Usa o método POST
      method: "POST",
      // Avisa que o corpo é JSON
      headers: { "Content-Type": "application/json" },
      // Converte o texto para JSON
      body: JSON.stringify({ texto: texto }),
    });
    // Erro 422: a mensagem não passou na validação da API
    if (resposta.status === 422) {
      // Mostra um erro em linguagem simples
      mostrarErro("A mensagem não pôde ser analisada. Confira se ela tem texto e menos de 2000 letras.");
      // Para aqui
      return;
    }
    // Erro 503: o modelo ainda não foi treinado
    if (resposta.status === 503) {
      // Mostra um erro em linguagem simples
      mostrarErro("O sistema ainda não está pronto. Tente de novo mais tarde.");
      // Para aqui
      return;
    }
    // Erro 429: o visitante passou do limite de verificações
    if (resposta.status === 429) {
      // Mostra um erro em linguagem simples
      mostrarErro("Muitas verificações em pouco tempo. Aguarde um minuto e tente de novo.");
      // Para aqui
      return;
    }
    // Qualquer outro erro do servidor
    if (!resposta.ok) {
      // Mostra um erro genérico
      mostrarErro("Algo deu errado do nosso lado. Tente de novo em instantes.");
      // Para aqui
      return;
    }
    // Lê o resultado em JSON
    const dados = await resposta.json();
    // Mostra o resultado na tela
    mostrarResultado(dados);
  // Trata falhas de conexão com o servidor
  } catch (erro) {
    // Mostra um erro em linguagem simples
    mostrarErro("Não consegui falar com o servidor. Confira se ele está ligado e tente de novo.");
  // Roda sempre no fim, com sucesso ou erro
  } finally {
    // Reativa o botão
    botaoVerificar.disabled = false;
    // Devolve o texto original ao botão
    botaoVerificar.textContent = "Verificar mensagem";
  }
});