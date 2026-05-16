from app.models.user_model import (
    create_cliente,
    create_dependente,
    create_pet,
    find_user_by_email,
    find_user_by_cpf,
    find_user_by_telefone,
    salvar_consentimento,
    revogar_consentimento,
    update_cliente,                                              # NOVO
    buscar_consentimento_ativo as _buscar_consentimento_ativo,
)

from app.database import get_connection
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from email.mime.text import MIMEText
from flask import request, session, flash, redirect, url_for
import random, smtplib, os


ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=8
)


# =========================
# BUSCAR CONSENTIMENTO ATIVO
# =========================
def buscar_consentimento_ativo(cliente_id):
    return _buscar_consentimento_ativo(cliente_id)


# =========================
# CADASTRAR USUÁRIO
# =========================
def cadastrar_usuario(form):

    conn   = None
    cursor = None

    try:

        if not form.get("termos"):
            return {"success": False, "erro": "Você precisa aceitar os termos."}

        senha     = form.get("senha")
        senha_ver = form.get("senhaVER")

        if senha != senha_ver:
            return {"success": False, "erro": "As senhas não coincidem"}

        if find_user_by_email(form.get("email")):
            return {"success": False, "erro": "Email já cadastrado"}

        if find_user_by_cpf(form.get("cpf")):
            return {"success": False, "erro": "CPF já cadastrado"}

        if find_user_by_telefone(form.get("telefone")):
            return {"success": False, "erro": "Telefone já cadastrado"}

        senha_hash = ph.hash(form.get("senha"))

        data = {
            "nome":            form.get("nome"),
            "telefone":        form.get("telefone"),
            "email":           form.get("email"),
            "senha":           senha_hash,
            "cpf":             form.get("cpf"),
            "cep":             form.get("cep"),
            "nome_dependente": form.get("nome_dependente"),
            "data_nascimento": form.get("data_nascimento"),
            "parentesco":      form.get("parentesco"),
            "nome_pet":        form.get("nome_pet"),
            "especie":         form.get("especie"),
            "raca":            form.get("raca"),
        }

        conn, cursor, cliente_id = create_cliente(data)

        if form.get("nome_dependente"):
            create_dependente(cursor, data, cliente_id)

        if form.get("nome_pet"):
            create_pet(cursor, data, cliente_id)

        salvar_consentimento(
            cursor=cursor,
            cliente_id=cliente_id,
            aceitou=True,
            versao_termo="1.0",
            ip_aceite=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )

        conn.commit()
        return {"success": True}

    except Exception:
        import traceback
        traceback.print_exc()
        if conn: conn.rollback()
        return {"success": False}

    finally:
        try:
            if cursor: cursor.close()
            if conn:   conn.close()
        except Exception:
            pass


# =========================
# LOGIN
# =========================
def realizar_login(form):

    email = form.get("email")
    senha = form.get("senha")

    usuario = find_user_by_email(email)

    if not usuario:
        return {"success": False, "erro": "Usuário não encontrado"}

    try:
        ph.verify(usuario["senha"], senha)
    except Exception:
        return {"success": False, "erro": "Senha incorreta"}

    return {"success": True, "usuario": usuario}


# =========================
# 2FA
# =========================
def gerar_codigo_2fa():
    codigo    = str(random.randint(100000, 999999))
    expiracao = datetime.now() + timedelta(minutes=5)
    return codigo, expiracao


def enviar_codigo_email(destinatario, codigo):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha     = os.getenv("EMAIL_SENHA")

    msg            = MIMEText(f"Seu código de verificação é: {codigo}")
    msg["Subject"] = "Código de verificação"
    msg["From"]    = remetente
    msg["To"]      = destinatario

    with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.send_message(msg)


# =========================
# REVOGAR ACEITE
# =========================
def revogar_aceite_controller(session):

    cliente_id = session.get("usuario_id")

    if not cliente_id:
        return {"success": False}

    try:
        revogar_consentimento(cliente_id)
        return {"success": True}
    except Exception:
        return {"success": False}


# =========================
# ACEITAR NOVAMENTE
# =========================
def aceitar_termos_novamente(session, request):

    cliente_id = session.get("usuario_id")

    if not cliente_id:
        return {"success": False}

    conn   = None
    cursor = None

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        salvar_consentimento(
            cursor=cursor,
            cliente_id=cliente_id,
            aceitou=True,
            versao_termo="1.0",
            ip_aceite=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )

        conn.commit()
        return {"success": True}

    except Exception:
        if conn: conn.rollback()
        return {"success": False}

    finally:
        try:
            if cursor: cursor.close()
            if conn:   conn.close()
        except Exception:
            pass


# =========================
# SALVAR DEPENDENTE
# =========================
def salvar_dependente_controller(session, form):

    cliente_id = session.get("usuario_id")

    if not cliente_id:
        return {"success": False}

    conn   = None
    cursor = None

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        data = {
            "nome_dependente": form.get("nome_dependente"),
            "data_nascimento": form.get("data_nascimento"),
            "parentesco":      form.get("parentesco"),
        }

        create_dependente(cursor, data, cliente_id)
        conn.commit()

        session["usuario_dependente"]      = data["nome_dependente"]
        session["usuario_parentesco"]      = data["parentesco"]
        session["usuario_data_nascimento"] = data["data_nascimento"]

        return {"success": True}

    except Exception:
        import traceback
        traceback.print_exc()
        if conn: conn.rollback()
        return {"success": False}

    finally:
        try:
            if cursor: cursor.close()
            if conn:   conn.close()
        except Exception:
            pass


# =========================
# SALVAR PET
# =========================
def salvar_pet_controller(session, form):

    cliente_id = session.get("usuario_id")

    if not cliente_id:
        return {"success": False}

    conn   = None
    cursor = None

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        data = {
            "nome_pet": form.get("nome_pet"),
            "especie":  form.get("especie"),
            "raca":     form.get("raca"),
        }

        create_pet(cursor, data, cliente_id)
        conn.commit()

        session["usuario_pet"]     = data["nome_pet"]
        session["usuario_especie"] = data["especie"]
        session["usuario_raca"]    = data["raca"]

        return {"success": True}

    except Exception:
        import traceback
        traceback.print_exc()
        if conn: conn.rollback()
        return {"success": False}

    finally:
        try:
            if cursor: cursor.close()
            if conn:   conn.close()
        except Exception:
            pass


# =========================
# EDITAR DADOS CADASTRAIS
# =========================
def editar_dados_controller(session, form):
    """
    Atualiza nome, telefone, email e cep.
    Valida duplicidade de email e telefone contra outros usuários.
    Atualiza a sessão após salvar com sucesso.
    CPF nunca é alterado.
    """

    cliente_id = session.get("usuario_id")

    if not cliente_id:
        return {"success": False, "erro": "Sessão inválida."}

    novo_nome     = form.get("nome",     "").strip()
    novo_telefone = form.get("telefone", "").strip()
    novo_email    = form.get("email",    "").strip()
    novo_cep      = form.get("cep",      "").strip()

    if not all([novo_nome, novo_telefone, novo_email, novo_cep]):
        return {"success": False, "erro": "Todos os campos são obrigatórios."}

    # Verifica se o email já pertence a outro usuário
    usuario_email = find_user_by_email(novo_email)
    if usuario_email and str(usuario_email["id"]) != str(cliente_id):
        return {"success": False, "erro": "Este e-mail já está em uso."}

    # Verifica se o telefone já pertence a outro usuário
    usuario_tel = find_user_by_telefone(novo_telefone)
    if usuario_tel and str(usuario_tel["id"]) != str(cliente_id):
        return {"success": False, "erro": "Este telefone já está em uso."}

    try:
        update_cliente(cliente_id, {
            "nome":     novo_nome,
            "telefone": novo_telefone,
            "email":    novo_email,
            "cep":      novo_cep,
        })

        # Atualiza sessão para refletir imediatamente sem novo login
        session["usuario_nome"]     = novo_nome
        session["usuario_telefone"] = novo_telefone
        session["usuario_email"]    = novo_email
        session["usuario_cep"]      = novo_cep

        return {"success": True}

    except Exception:
        import traceback
        traceback.print_exc()
        return {"success": False, "erro": "Erro ao atualizar os dados."}