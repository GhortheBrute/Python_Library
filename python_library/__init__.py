import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Carrega as variáveis do .env
load_dotenv()

# Inicializa o 'db'. Note que não o ligamos ao 'app' ainda.
# Isso evita problemas de "importação circular".
db = SQLAlchemy()

def create_app():
    """
    Função 'Application Factory'.
    Ela cria e configura a instância do app Flask.
    """
    app = Flask(__name__)

    # --- Configuração do Banco de Dados ---
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")

    # -- Codifica a senha --
    safe_user = quote_plus(DB_USER)
    safe_pass = quote_plus(DB_PASS)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{safe_user}:{safe_pass}@{DB_HOST}/{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Conecta o 'db' ao 'app' que acabamos de criar
    db.init_app(app)

    # --- Registrar Models e Rotas ---
    # Importamos aqui para garantir que o 'db' esteja pronto
    with app.app_context():
        # Importa seus modelos
        from . import models

        # Cria todas as tabelas no banco de dados
        # (se elas ainda não existirem)
        db.create_all()

    # Importa e registra as rotas (views)
    from . import routes
    app.register_blueprint(routes.bp) # Vamos criar isso depois

    # Retorna o app pronto
    return app