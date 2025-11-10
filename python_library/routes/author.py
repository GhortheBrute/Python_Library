import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Author

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('authors', __name__, url_prefix='/api/authors')


@bp.route('/', methods=['POST'])
def create_author():
    """
    Endpoint for creating an author
    Awaits a JSON with author details and address
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação simples
    required_fields = ['FName', 'LName']

    # Validação de dados Pessoa Física
    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"Required field {field} is missing"}), 400

    # Transação de Banco de Dados
    try:
        # Criar o Author
        new_author = Author(
            FName='FName',
            MName='MName',
            LName='LName'
        )
        db.session.add(new_author)

        # Se tudo certo, comitar a transação
        db.session.commit()

        return jsonify({'message': 'Author successfully created'}), 201

    except Exception as e:
        # Se algo deu errado, reverter tudo
        db.session.rollback()
        logging.error(f"Failed to create author: {e}")
        return jsonify({"error": f"Failed to create author: {e}"}), 500


@bp.route('/', methods=['GET'])
def get_authors():
    """
    Endpoint for getting all authors
    Accepts a 'status' query param:
    - ?status=active (default)
    - ?status=inactive
    - ?status=all
    """
    try:
        # Pegamos o parâmetro da url
        # Se nada for passado, o valor padrão é 'active'
        status_filter = request.args.get('status', 'active')

        # 1. Fazemos a consulta unindo as 4 tabelas de Clientes
        # (Client, ClientFP, ClientJP, Address)
        query = db.session.query(Author)

        # Adicionamos o filtro de status
        if status_filter == 'active':
            query = query.filter(Author.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Author.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        # 2. Formatamos os resultados para JSON
        output = []
        for author in results:
            author_data = {
                'idAuthor': author.idAuthor,
                'Name': f"{author.LName}, {author.FName} {author.MName} ",
            }
            output.append(author_data)

        return jsonify({'authors': output}), 200

    except Exception as e:
        logging.error(f"Failed to get authors: {e}")
        return jsonify({"error": f"Failed to get authors"}), 500


@bp.route('/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """
    Endpoint for getting a specific author by ID
    """
    try:
        # 1. Fazemos a mesma consulta, mas filtramos pelo ID
        result = get_author_by_id(author_id)

        # 2. Verificamos se o cliente foi encontrado
        if not result:
            return jsonify({"error": "Author not found"}), 404

        # 3. Desempacotamos os resultados
        author = result

        # 4. Formatamos o JSON de resposta
        author_data = {
            'idAuthor': author.idAuthor,
            'Name': f"{author.LName}, {author.FName} {author.MName} ",
        }
        return jsonify(author_data), 200

    except Exception as e:
        logging.error(f"Failed to get author: {e}")
        return jsonify({"error": f"Failed to get author: {e}"}), 500


@bp.route('/<int:author_id>', methods=['PUT', 'PATCH'])
def update_author(author_id):
    """
    Endpoint for updating an author
    """

    # 1. Obter os dados da requisição
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # 2. -- Reaproveitando o código ---
        result = get_author_by_id(author_id)

        if not result:
            return jsonify({"error": "Client not found"}), 404

        # 3. Desempacotando os objetos
        author = result

        # 4. Atualização
        # Atualizamos os campos principais do Cliente
        # data.get('Phone', client.Phone) significa:
        # "Pegue o 'Phone' do JSON, se não existir, use o valor original
        author.FName = data.get('FName', author.FName)
        author.MName = data.get('MName', author.MName)
        author.LName = data.get('LName', author.LName)

        # 5. Salvar as mudanças no banco
        db.session.commit()

        return jsonify({"error": "Author updated successfully"}), 200
    except Exception as e:
        logging.error(f"Failed to update author: {e}")
        return jsonify({"error": f"Failed to update author: {e}"}), 500


@bp.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """
    Endpoint for deleting an author
    Verify if the author has pendencies
    """
    # Soft Delete
    author = db.session.query(Author).filter_by(idAuthor=author_id).first()
    if not author:
        return jsonify({"error": "Author not found"}), 404

    # Apenas marca como inativo
    author.is_active = False
    db.session.commit()

    return '', 204

def get_author_by_id(author_id):
    return db.session.query(
        Author
    ).filter(
        Author.idAuthor == author_id,
        ).first()  # .first() pega apenas um

def get_author_by_name(author_name):
    return db.session.query(
        Author
    ).filter(
        Author.FName == author_name
    ).first()