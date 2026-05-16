from flask import session, make_response
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from io import BytesIO
from datetime import datetime


def exportar_pdf_controller():

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)

    # =========================
    # CORES
    # =========================
    azul = HexColor("#ffa500")
    cinza = HexColor("#555555")
    branco = HexColor("#FFFFFF")

    # =========================
    # CABEÇALHO
    # =========================
    pdf.setFillColor(azul)

    pdf.rect(0, 770, 600, 70, fill=1)

    pdf.setFillColor(branco)

    pdf.setFont("Helvetica-Bold", 22)

    pdf.drawString(50, 795, "Dados do Perfil")

    # =========================
    # DADOS
    # =========================
    y = 730

    campos = [

        ("ID", session.get("usuario_id")),
        ("Nome", session.get("usuario_nome")),
        ("E-mail", session.get("usuario_email")),
        ("Telefone", session.get("usuario_telefone")),
        ("CPF", session.get("usuario_cpf")),
        ("CEP", session.get("usuario_cep")),

        ("Dependente", session.get("usuario_dependente")),
        ("Parentesco", session.get("usuario_parentesco")),
        ("Data de nascimento", session.get("usuario_data_nascimento")),

        ("Pet", session.get("usuario_pet")),
        ("Espécie", session.get("usuario_especie")),
        ("Raça", session.get("usuario_raca"))
    ]

    # MOSTRA SOMENTE CAMPOS PREENCHIDOS
    for titulo, valor in campos:

        if valor:

            # TÍTULO
            pdf.setFillColor(azul)

            pdf.setFont("Helvetica-Bold", 12)

            pdf.drawString(
                50,
                y,
                f"{titulo}:"
            )

            # VALOR
            pdf.setFillColor(cinza)

            pdf.setFont("Helvetica", 12)

            pdf.drawString(
                170,
                y,
                str(valor)
            )

            y -= 28

    # =========================
    # LINHA FINAL
    # =========================
    pdf.setStrokeColor(azul)

    pdf.line(50, 80, 550, 80)

    # =========================
    # RODAPÉ
    # =========================
    data_exportacao = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf.setFillColor(cinza)

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        50,
        55,
        "SAECA"
    )

    pdf.setFont("Helvetica", 10)

    pdf.drawRightString(
        550,
        55,
        f"Exportado em: {data_exportacao}"
    )

    # =========================
    # FINALIZA PDF
    # =========================
    pdf.save()

    buffer.seek(0)

    response = make_response(
        buffer.getvalue()
    )

    response.headers["Content-Type"] = "application/pdf"

    response.headers["Content-Disposition"] = (
        "attachment; filename=perfil.pdf"
    )

    return response