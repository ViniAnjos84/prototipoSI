from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from app.utils.auth_decorators import login_required
from app.controllers.pdf_controller import exportar_pdf_controller

from app.controllers.user_controller import (
    buscar_consentimento_ativo,
    revogar_aceite_controller,
    aceitar_termos_novamente,
    salvar_dependente_controller,
    salvar_pet_controller,
    editar_dados_controller,         # NOVO
)

main_bp = Blueprint("main", __name__)


# ======================
# PERFIL
# ======================
@main_bp.route("/user/meu-perfil")
@login_required
def user_meuPerfil():

    cliente_id    = session.get("usuario_id")
    consentimento = buscar_consentimento_ativo(cliente_id)

    return render_template(
        "users/meu-perfil.html",
        consentimento_ativo=(consentimento is not None)
    )


# ======================
# EDITAR DADOS CADASTRAIS
# ======================
@main_bp.route("/user/editar-dados", methods=["POST"])
@login_required
def editar_dados():

    resultado = editar_dados_controller(session, request.form)

    if resultado["success"]:
        flash("Dados atualizados com sucesso!", "success")
    else:
        flash(resultado.get("erro", "Erro ao atualizar os dados."), "danger")

    return redirect(url_for("main.user_meuPerfil"))


# ======================
# INDEX
# ======================
@main_bp.route("/index")
@main_bp.route("/")
def index():
    return render_template("index.html")


# ======================
# DASHBOARDS
# ======================
@main_bp.route("/indexAdmin")
@login_required
def indexAdm():
    return render_template("indexAdm.html")


@main_bp.route("/indexUsers")
@login_required
def indexUsers():
    return render_template("indexUsers.html")


# ======================
# ADMIN
# ======================
@main_bp.route("/admin/cadastro")
@login_required
def adm_cadastro():
    return render_template("admin/adm-cadastro.html")


@main_bp.route("/admin/notificacoes")
@login_required
def adm_notificacoes():
    return render_template("admin/adm-notificacoes.html")


@main_bp.route("/admin/relatorio")
@login_required
def adm_relatorio():
    return render_template("admin/adm-relatorio.html")


@main_bp.route("/admin/usuarios")
@login_required
def adm_usuarios():
    return render_template("admin/adm-usuarios.html")


@main_bp.route("/admin/agendamentos")
@login_required
def adm_visualizar_agd():
    return render_template("admin/adm-visualizarAgd.html")


# ======================
# FORMULÁRIOS ADMIN
# ======================
@main_bp.route("/admin/form/consulta-medica")
@login_required
def form_consulta_medica():
    return render_template("admin/formConsultaMedica.html")


@main_bp.route("/admin/form/consulta-vet")
@login_required
def form_consulta_vet():
    return render_template("admin/formConsultaVet.html")


@main_bp.route("/admin/form/cursos")
@login_required
def form_cursos():
    return render_template("admin/formCursos.html")


@main_bp.route("/admin/form/eventos")
@login_required
def form_eventos():
    return render_template("admin/formEventos.html")


@main_bp.route("/admin/form/oficinas")
@login_required
def form_oficinas():
    return render_template("admin/formOficina.html")


# ======================
# USERS
# ======================
@main_bp.route("/user/acessibilidade")
@login_required
def user_acessibilidade():
    return render_template("users/acessibilidade.html")


@main_bp.route("/user/consultas-medicas")
@login_required
def user_consultas_medicas():
    return render_template("users/consultas-medicas.html")


@main_bp.route("/user/consultas-veterinarias")
@login_required
def user_consultas_vet():
    return render_template("users/consultas-veterinarias.html")


@main_bp.route("/user/cursos")
@login_required
def user_cursos():
    return render_template("users/cursos.html")


@main_bp.route("/user/eventos")
@login_required
def user_eventos():
    return render_template("users/eventos.html")


@main_bp.route("/user/agendamentos")
@login_required
def user_agendamentos():
    return render_template("users/meus-agendamentos.html")


@main_bp.route("/user/notificacoes")
@login_required
def user_notificacoes():
    return render_template("users/notificacoes.html")


@main_bp.route("/user/oficinas")
@login_required
def user_oficinas():
    return render_template("users/oficinas.html")


@main_bp.route("/user/servicos")
@login_required
def user_servicos():
    return render_template("users/servicos.html")


# ======================
# EXPORTAR PDF
# ======================
@main_bp.route("/user/exportar-pdf")
@login_required
def exportar_pdf():
    return exportar_pdf_controller()


# ======================
# TERMOS
# ======================
@main_bp.route("/termos")
def termos_uso():
    return render_template("termos.html")


# ======================
# CONSENTIMENTO - REVOGAR
# ======================
@main_bp.route("/revogar-consentimento", methods=["POST"])
@login_required
def revogar_consentimento_route():

    resultado = revogar_aceite_controller(session)

    if resultado["success"]:
        flash("Consentimento revogado com sucesso.", "warning")
    else:
        flash("Erro ao revogar consentimento.", "danger")

    return redirect(url_for("main.user_meuPerfil"))


# ======================
# CONSENTIMENTO - ACEITAR NOVAMENTE
# ======================
@main_bp.route("/aceitar-termos", methods=["POST"])
@login_required
def aceitar_termos_route():

    resultado = aceitar_termos_novamente(session, request)

    if resultado["success"]:
        flash("Termos aceitos com sucesso!", "success")
    else:
        flash("Erro ao aceitar os termos.", "danger")

    return redirect(url_for("main.user_meuPerfil"))


# ======================
# SALVAR DEPENDENTE
# ======================
@main_bp.route("/user/salvar-dependente", methods=["POST"])
@login_required
def salvar_dependente():

    resultado = salvar_dependente_controller(session, request.form)

    if resultado["success"]:
        flash("Dependente cadastrado com sucesso!", "success")
    else:
        flash("Erro ao cadastrar dependente.", "danger")

    return redirect(url_for("main.user_meuPerfil"))


# ======================
# SALVAR PET
# ======================
@main_bp.route("/user/salvar-pet", methods=["POST"])
@login_required
def salvar_pet():

    resultado = salvar_pet_controller(session, request.form)

    if resultado["success"]:
        flash("Pet cadastrado com sucesso!", "success")
    else:
        flash("Erro ao cadastrar pet.", "danger")

    return redirect(url_for("main.user_meuPerfil"))