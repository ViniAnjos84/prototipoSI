const senha = document.getElementById("senha");
const senhaVER = document.getElementById("senhaVER");
const erroSenha = document.getElementById("erroSenha");

const requisitos = {
  tamanho: document.getElementById("req-tamanho"),
  maiuscula: document.getElementById("req-maiuscula"),
  minuscula: document.getElementById("req-minuscula"),
  numero: document.getElementById("req-numero"),
  especial: document.getElementById("req-especial")
};

function validarSenha() {

  const valor = senha.value;

  atualizarRequisito(
    requisitos.tamanho,
    valor.length >= 8
  );

  atualizarRequisito(
    requisitos.maiuscula,
    /[A-Z]/.test(valor)
  );

  atualizarRequisito(
    requisitos.minuscula,
    /[a-z]/.test(valor)
  );

  atualizarRequisito(
    requisitos.numero,
    /\d/.test(valor)
  );

  atualizarRequisito(
    requisitos.especial,
    /[^A-Za-z0-9]/.test(valor)
  );

}

function atualizarRequisito(elemento, valido) {

  elemento.textContent =
    elemento.textContent.replace("❌", "")
                         .replace("✅", "");

  elemento.textContent =
    (valido ? "✅ " : "❌ ") +
    elemento.textContent;

}

function verificarSenhas() {

  if (
    senhaVER.value &&
    senha.value !== senhaVER.value
  ) {

    erroSenha.style.display = "block";

  } else {

    erroSenha.style.display = "none";

  }

}

senha.addEventListener("input", () => {
  validarSenha();
  verificarSenhas();
});

senhaVER.addEventListener("input", verificarSenhas);