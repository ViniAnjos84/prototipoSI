from app import create_app

# Se quiser evoluir mais um nível (vale muito a pena), esses são os próximos passos naturais:
# 🔐 implementar controle de sessão completo (login + logout + proteção de rotas)
# 🛡️ criar um decorator tipo login_required
# 🧹 padronizar retorno dos controllers (ex: sempre {success, data, error})
# 📦 organizar melhor os models (evitar repetir conexão/cursor)
# ⚙️ mover configs sensíveis pro .env

#
#
#
#

# 1. python -m venv venv
# 2. venv/Scripts/Activate.ps1
# 3. pip install -r requirements.txt

app = create_app()
app.run(debug=True)

