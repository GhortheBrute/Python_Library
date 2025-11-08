from flask import Blueprint

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('routes', __name__)

@bp.route('/')
def hello_world():
    return 'Olá mundo!'