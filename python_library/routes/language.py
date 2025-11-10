import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Language

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('languages', __name__, url_prefix='/api/languages')


@bp.route('/', methods=['POST'])
def create_language():
    """
    Endpoint for creating a language
    Awaits a JSON with language details and address
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação simples
    required_fields = ['Code', 'Name']

    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"Required field {field} is missing"}), 400

    # Transação de Banco de Dados
    try:
        # Criar o Language
        new_language = Language(
            Code='Code',
            Name='Name'
        )
        db.session.add(new_language)

        # Se tudo certo, comitar a transação
        db.session.commit()

        return jsonify({'message': 'Language successfully created'}), 201

    except Exception as e:
        # Se algo deu errado, reverter tudo
        db.session.rollback()
        logging.error(f"Failed to create language: {e}")
        return jsonify({"error": f"Failed to create language: {e}"}), 500


@bp.route('/', methods=['GET'])
def get_languages():
    """
    Endpoint for getting all languages
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
        query = db.session.query(Language)

        # Adicionamos o filtro de status
        if status_filter == 'active':
            query = query.filter(Language.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Language.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        # 2. Formatamos os resultados para JSON
        output = []
        for language in results:
            language_data = {
                'idLanguage': language.idLanguage,
                'Code': language.Code,
                'Name': language.Name
            }
            output.append(language_data)

        return jsonify({'languages': output}), 200

    except Exception as e:
        logging.error(f"Failed to get languages: {e}")
        return jsonify({"error": f"Failed to get languages"}), 500


@bp.route('/<int:language_id>', methods=['GET'])
def get_language(language_id):
    """
    Endpoint for getting a specific language by ID
    """
    try:
        # 1. Fazemos a mesma consulta, mas filtramos pelo ID
        result = get_language_by_id(language_id)

        # 2. Verificamos se o cliente foi encontrado
        if not result:
            return jsonify({"error": "Language not found"}), 404

        # 3. Desempacotamos os resultados
        language = result

        # 4. Formatamos o JSON de resposta
        language_data = {
            'idLanguage': language.idLanguage,
            'Code': language.Code,
            'Name': language.Name
        }
        return jsonify(language_data), 200

    except Exception as e:
        logging.error(f"Failed to get language: {e}")
        return jsonify({"error": f"Failed to get language: {e}"}), 500


@bp.route('/<int:language_id>', methods=['PUT', 'PATCH'])
def update_language(language_id):
    """
    Endpoint for updating a language
    """

    # 1. Obter os dados da requisição
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # 2. -- Reaproveitando o código ---
        result = get_language_by_id(language_id)

        if not result:
            return jsonify({"error": "Client not found"}), 404

        # 3. Desempacotando os objetos
        language = result

        # 4. Atualização
        # Atualizamos os campos principais do Cliente
        # data.get('Phone', client.Phone) significa:
        # "Pegue o 'Phone' do JSON, se não existir, use o valor original
        language.Name = data.get('Name', language.Name)
        language.Code = data.get('Code', language.Code)

        # 5. Salvar as mudanças no banco
        db.session.commit()

        return jsonify({"error": "Language updated successfully"}), 200
    except Exception as e:
        logging.error(f"Failed to update language: {e}")
        return jsonify({"error": f"Failed to update language: {e}"}), 500


@bp.route('/<int:language_id>', methods=['DELETE'])
def delete_language(language_id):
    """
    Endpoint for deleting a language
    Verify if the language has pendencies
    """
    # Soft Delete
    language = db.session.query(Language).filter_by(idLanguage=language_id).first()
    if not language:
        return jsonify({"error": "Language not found"}), 404

    # Apenas marca como inativo
    language.is_active = False
    db.session.commit()

    return '', 204

def get_language_by_id(language_id):
    return db.session.query(
        Language
    ).filter(
        Language.idLanguage == language_id,
        ).first()  # .first() pega apenas um

def get_language_by_name(language_name):
    return db.session.query(
        Language
    ).filter(
        Language.Name == language_name
    ).first()

def get_language_by_code(language_code):
    return db.session.query(
        Language
    ).filter(
        Language.Code == language_code
    ).first()