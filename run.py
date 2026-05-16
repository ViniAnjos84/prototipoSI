from app import create_app

# Se quiser evoluir mais um nível (vale muito a pena), esses são os próximos passos naturais:
# 🧹 padronizar retorno dos controllers (ex: sempre {success, data, error})
# 📦 organizar melhor os models (evitar repetir conexão/cursor)

# 1. python -m venv venv
# 2. venv/Scripts/Activate.ps1
# 3. pip install -r requirements.txt

app = create_app()
app.run(debug=True)

