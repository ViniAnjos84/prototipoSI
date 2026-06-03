from flask import Blueprint, render_template, request, redirect, session, url_for
from app import limiter
from app.models.user_model import find_user_by_email, create_log_auth, create_log_2fa
from app.controllers.user_controller import (
    cadastrar_usuario,
    realizar_login,
    gerar_codigo_2fa,
    enviar_codigo_email,
    redefinir_senha
)

from datetime import datetime

auth_bp = Blueprint("auth", __name__)


# Custom key_func para amarrar o rate-limit ao IP e ao e-mail do formulário simultaneamente.
# Impede que scripts maliciosos limpem cookies para burlar as tentativas.
def login_rate_key():
    email = request.form.get("email", "")
    return f"{request.remote_addr}:{email}"

# ========================
# CADASTRO
# ========================
@auth_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():

    if request.method == "GET":
        return render_template("cadastro.html")

    result = cadastrar_usuario(request.form)

    if result["success"]:
        return render_template(
            "cadastro.html",
            mensagem="Cadastro realizado com sucesso!",
            tipo="sucesso"
        )

    return render_template(
        "cadastro.html",
        mensagem=result.get("erro", "Erro ao cadastrar!"),
        tipo="erro"
    )


# ========================
# LOGIN
# ========================
MAX_TENTATIVAS = 5
@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
@limiter.limit("20 per hour")
def login():

    if request.method == "GET":
        return render_template("login.html")

    # Verifica bloqueio com Flask Limiter
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    result = realizar_login(
        request.form,
        ip=ip,
        user_agent=user_agent
    )

    if not result["success"]:
        return render_template(
            "login.html",
            mensagem=result["erro"],
            tipo="erro"
        )

    usuario = result["usuario"]
    codigo, expiracao = gerar_codigo_2fa()

    session["usuario_temp_id"]                = usuario["id"]
    session["usuario_temp_nome"]              = usuario["nome"]
    session["usuario_temp_email"]             = usuario["email"]
    session["usuario_temp_telefone"]          = usuario["telefone"]
    session["usuario_temp_cep"]               = usuario["cep"]
    session["usuario_temp_cpf"]               = usuario["cpf"]

    session["usuario_temp_dependente"]        = usuario.get("nome_dependente")
    session["usuario_temp_parentesco"]        = usuario.get("parentesco")
    session["usuario_temp_data_nascimento"]   = usuario.get("data_nascimento")
    session["usuario_temp_pet"]               = usuario.get("nome_pet")
    session["usuario_temp_especie"]           = usuario.get("especie")
    session["usuario_temp_raca"]              = usuario.get("raca")

    session["codigo_2fa"]    = codigo
    session["codigo_expira"] = expiracao.strftime("%Y-%m-%d %H:%M:%S")

    enviar_codigo_email(usuario["email"], codigo)

    return redirect(url_for("auth.verificar_2fa"))


# ========================
# VERIFICAR 2FA
# Requisito 1.6: Validação do 2FA após autenticação primária
# Requisito 1.8: Evidências funcionais (prints, logs ou testes)
# ========================
@auth_bp.route("/verificar-2fa", methods=["GET", "POST"])
def verificar_2fa():

    if request.method == "GET":
        return render_template("2fa.html")

    codigo_digitado = request.form["codigo"]
    codigo_salvo    = session.get("codigo_2fa")
    expiracao       = session.get("codigo_expira")
    email           = session.get("usuario_temp_email")

    if not codigo_salvo:

        # Requisito 5.2: Logs de falhas e 2FA registrados
        create_log_2fa(
            email=email,
            sucesso=False,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            motivo_falha="Sessao expirada"
        )

        return render_template("2fa.html", mensagem="Sessão expirada.", tipo="erro")

    if datetime.now() > datetime.strptime(expiracao, "%Y-%m-%d %H:%M:%S"):
        
        # Requisito 5.2: Logs de falhas e 2FA registrados
        create_log_2fa(
            email=email,
            sucesso=False,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            motivo_falha="Codigo expirado"
        )

        session.clear()
        return render_template("2fa.html", mensagem="Código expirado.", tipo="erro")

    if int(codigo_digitado) == codigo_salvo:

        # Requisito 5.2: Logs de falhas e 2FA registrados
        create_log_2fa(
            email=email,
            sucesso=True,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )

        session.permanent = True

        session["usuario_id"]             = session.pop("usuario_temp_id")
        session["usuario_nome"]           = session.pop("usuario_temp_nome")
        session["usuario_email"]          = session.pop("usuario_temp_email")
        session["usuario_telefone"]       = session.pop("usuario_temp_telefone")
        session["usuario_cep"]            = session.pop("usuario_temp_cep")
        session["usuario_cpf"]            = session.pop("usuario_temp_cpf")

        session["usuario_dependente"]       = session.pop("usuario_temp_dependente", None)
        session["usuario_parentesco"]       = session.pop("usuario_temp_parentesco", None)
        session["usuario_data_nascimento"]  = session.pop("usuario_temp_data_nascimento", None)
        session["usuario_pet"]              = session.pop("usuario_temp_pet", None)
        session["usuario_especie"]          = session.pop("usuario_temp_especie", None)
        session["usuario_raca"]             = session.pop("usuario_temp_raca", None)

        session.pop("codigo_2fa", None)
        session.pop("codigo_expira", None)

        return redirect(url_for("main.indexUsers"))

    # Requisito 5.2: Logs de falhas e 2FA registrados
    create_log_2fa(
        email=email,
        sucesso=False,
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
        motivo_falha="Codigo invalido"
    )

    return render_template(
        "2fa.html",
        mensagem="Código inválido.",
        tipo="erro"
    )


# ========================
# RECUPERACAO DE SENHA
# Requisito 2.1: Funcionalidade de recuperação de senha
# ========================
@auth_bp.route("/recuperar-senha", methods=["GET", "POST"])
def recuperar_senha():

    if request.method == "GET":
        return render_template("recuperarSenha.html")

    email = request.form["email"]
    ip = request.remote_addr

    user_agent = request.headers.get("User-Agent")
    usuario = find_user_by_email(email)

    # Requisito 5.2: Logs de falhas e 2FA registrados
    if not usuario:
        create_log_auth(
            email=email,
            sucesso=False,
            ip=ip,
            user_agent=user_agent,
            motivo_falha="Tentativa de recuperação: E-mail não localizado no sistema"
        )

        return render_template(
            "recuperarSenha.html",
            mensagem="Email não encontrado",
            tipo="erro"
        )

    codigo, expiracao = gerar_codigo_2fa()

    # Requisito 2.3: Token com tempo de expiração
    session["email_recuperacao"] = email
    session["reset_codigo"]      = codigo
    session["reset_expira"]      = expiracao.strftime("%Y-%m-%d %H:%M:%S")

    enviar_codigo_email(email, codigo)

    # Requisito 2.6: Registro de solicitação de recuperação em log
    create_log_auth(
        email=email,
        sucesso=True,
        ip=ip,
        user_agent=user_agent,
        motivo_falha="Solicitação de redefinição de senha gerada com envio de token"
    )

    return redirect(url_for("auth.validar_codigo_recuperacao"))

@auth_bp.route("/validar-recuperacao", methods=["GET", "POST"])
def validar_codigo_recuperacao():

    if request.method == "GET":
        return render_template("validarCodigoRecuperacao.html")

    codigo_digitado = request.form["codigo"]
    codigo_salvo    = session.get("reset_codigo")
    expiracao       = session.get("reset_expira")
    email           = session.get("email_recuperacao", "desconhecido")
    ip              = request.remote_addr
    user_agent      = request.headers.get("User-Agent")

    # Requisito 2.5: Falha correta para token expirado
    if not codigo_salvo or not expiracao:

        session.clear()

        # Requisito 5.2: Logs de falhas e 2FA registrados
        create_log_auth(
            email=email,
            sucesso=False,
            ip=ip,
            user_agent=user_agent,
            motivo_falha="Falha na validação do token: Sessão inexistente ou expirada"
        )

        return render_template(
            "validarCodigoRecuperacao.html",
            mensagem="Sessão expirada. Solicite um novo código.",
            tipo="erro"
        )

    expiracao_datetime = datetime.strptime(expiracao, "%Y-%m-%d %H:%M:%S")

    if datetime.now() > expiracao_datetime:

        # Requisito 2.4: Token invalidado após uso
        session.pop("reset_codigo", None)
        session.pop("reset_expira", None)
        session.pop("email_recuperacao", None)

        # Requisito 5.2: Logs de falhas e 2FA registrados
        create_log_auth(
            email=email,
            sucesso=False,
            ip=ip,
            user_agent=user_agent,
            motivo_falha="Falha na validação do token: Janela de tempo esgotada"
        )

        return render_template(
            "validarCodigoRecuperacao.html",
            mensagem="Código expirado. Solicite outro código.",
            tipo="erro"
        )

    if codigo_digitado != codigo_salvo:
        
        # Requisito 5.2: Logs de falhas e 2FA registrados
        create_log_auth(
            email=email,
            sucesso=False,
            ip=ip,
            user_agent=user_agent,
            motivo_falha="Falha na validação do token: Token numérico digitado inválido"
        )

        return render_template(
            "validarCodigoRecuperacao.html",
            mensagem="Código inválido.",
            tipo="erro"
        )
    # Requisito 2.7: Log de sucesso na validação intermediária do token
    create_log_auth(
        email=email,
        sucesso=True,
        ip=ip,
        user_agent=user_agent,
        motivo_falha="Token de recuperação validado com sucesso"
    )    

    session["reset_validado"] = True
    session.pop("reset_codigo", None)
    session.pop("reset_expira", None)

    return redirect(url_for("auth.nova_senha"))

@auth_bp.route("/nova-senha", methods=["GET", "POST"])
def nova_senha():

    email          = session.get("email_recuperacao")
    reset_validado = session.get("reset_validado")
    ip             = request.remote_addr
    user_agent     = request.headers.get("User-Agent")

    if not email or not reset_validado:
        return redirect(url_for("auth.recuperar_senha"))

    if request.method == "GET":
        return render_template("novaSenha.html")

    elif request.method == "POST":

        resultado = redefinir_senha(
            email=email,
            form=request.form
        )

        # Requisito 2.7: Registro de sucesso/falha do processo
        # Requisito 5.2: Logs de falhas e 2FA registrados
        if not resultado["success"]:

            create_log_auth(
                email=email,
                sucesso=False,
                ip=ip,
                user_agent=user_agent,
                motivo_falha=f"Erro ao salvar nova senha: {resultado.get('erro')}"
            )

            return render_template(
                "novaSenha.html",
                mensagem=resultado["erro"],
                tipo="erro"
            )

        # Requisito 2.7: Registro de sucesso/falha do processo
        create_log_auth(
            email=email,
            sucesso=True,
            ip=ip,
            user_agent=user_agent,
            motivo_falha="Senha modificada e atualizada com sucesso no banco de dados"
        )

        session.pop("email_recuperacao", None)
        session.pop("reset_validado", None)

        return redirect(url_for("auth.login"))

    return render_template("novaSenha.html")


# ========================
# LOGOUT
# ========================
@auth_bp.route("/logout")
def logout():

    # Requisito 1.10 Invalidação de sessão no logout
    session.clear()
    return redirect("/")