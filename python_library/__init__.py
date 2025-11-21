import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from urllib.parse import quote_plus
from flasgger import Swagger
from flask_cors import CORS

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

    CORS(app)

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

    # Inicializa o Swagger
    swagger = Swagger(app)

    # --- Registrar Models e Rotas ---
    # Importamos aqui para garantir que o 'db' esteja pronto
    with app.app_context():
        # Importa seus modelos
        from . import models

        # Cria todas as tabelas no banco de dados
        # (se elas ainda não existirem)
        db.create_all()

    # Importa e registra as rotas (views)
    from .routes.author import bp as author_bp
    from .routes.branch import bp as branch_bp
    from .routes.book import bp as book_bp
    from .routes.client import bp as client_bp
    from .routes.collection import bp as collection_bp
    from .routes.loan import bp as loan_bp
    from .routes.physicalBook import bp as physical_book_bp
    from .routes.publisher import bp as publisher_bp
    from .routes.reserve import bp as reserve_bp
    from .routes.reports import bp as report_bp
    from .routes.review import bp as review_bp


    app.register_blueprint(author_bp)
    app.register_blueprint(branch_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(physical_book_bp)
    app.register_blueprint(publisher_bp)
    app.register_blueprint(reserve_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(review_bp)

    # -- INITIAL SEED --
    from . import seed
    seed.register_seed_command(app)
    # -- END OF SEED --

    # Retorna o app pronto
    return app