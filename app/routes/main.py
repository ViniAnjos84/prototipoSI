from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/index")
@main_bp.route("/")
def index():
    return render_template("index.html")

# ======================
# DASHBOARDS
# ======================
@main_bp.route("/indexAdmin")
def indexAdm():
    return render_template("indexAdm.html")

@main_bp.route("/indexUsers")
def indexUsers():
    return render_template("indexUsers.html")

# ======================
# ADMIN
# ======================
@main_bp.route("/admin/cadastro")
def adm_cadastro():
    return render_template("admin/adm-cadastro.html")

@main_bp.route("/admin/notificacoes")
def adm_notificacoes():
    return render_template("admin/adm-notificacoes.html")

@main_bp.route("/admin/relatorio")
def adm_relatorio():
    return render_template("admin/adm-relatorio.html")

@main_bp.route("/admin/usuarios")
def adm_usuarios():
    return render_template("admin/adm-usuarios.html")

@main_bp.route("/admin/agendamentos")
def adm_visualizar_agd():
    return render_template("admin/adm-visualizarAgd.html")

# ======================
# FORMULÁRIOS ADMIN
# ======================
@main_bp.route("/admin/form/consulta-medica")
def form_consulta_medica():
    return render_template("admin/formConsultaMedica.html")

@main_bp.route("/admin/form/consulta-vet")
def form_consulta_vet():
    return render_template("admin/formConsultaVet.html")

@main_bp.route("/admin/form/cursos")
def form_cursos():
    return render_template("admin/formCursos.html")

@main_bp.route("/admin/form/eventos")
def form_eventos():
    return render_template("admin/formEventos.html")

@main_bp.route("/admin/form/oficinas")
def form_oficinas():
    return render_template("admin/formOficina.html")

# ======================
# USERS
# ======================
@main_bp.route("/user/acessibilidade")
def user_acessibilidade():
    return render_template("users/acessibilidade.html")

@main_bp.route("/user/consultas-medicas")
def user_consultas_medicas():
    return render_template("users/consultas-medicas.html")

@main_bp.route("/user/consultas-veterinarias")
def user_consultas_vet():
    return render_template("users/consultas-veterinarias.html")

@main_bp.route("/user/cursos")
def user_cursos():
    return render_template("users/cursos.html")

@main_bp.route("/user/eventos")
def user_eventos():
    return render_template("users/eventos.html")

@main_bp.route("/user/agendamentos")
def user_agendamentos():
    return render_template("users/meus-agendamentos.html")

@main_bp.route("/user/notificacoes")
def user_notificacoes():
    return render_template("users/notificacoes.html")

@main_bp.route("/user/oficinas")
def user_oficinas():
    return render_template("users/oficinas.html")

@main_bp.route("/user/servicos")
def user_servicos():
    return render_template("users/servicos.html")

@main_bp.route("/user/meu-perfil")
def user_meuPerfil():
    return render_template("users/meu-perfil.html")

