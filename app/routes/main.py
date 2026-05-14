from flask import Blueprint, render_template
from app.utils.auth_decorators import login_required

main_bp = Blueprint("main", __name__)

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

@main_bp.route("/user/meu-perfil")
def user_meuPerfil():
    return render_template("users/meu-perfil.html")

