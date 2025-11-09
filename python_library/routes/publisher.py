import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Address, Publisher

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('publishers', __name__, url_prefix='/api/publishers')

@bp.route('/', methods=['POST'])
def create_publisher():
    """
    Endpoint for creating a publisher
    Awaits a JSON with publisher details and address
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação simples
    required_fields = ['Address', 'CNPJ', 'Name']

    # Validação de dados Pessoa Física
    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"Required field {field} is missing"}), 400

    # Transação de Banco de Dados
    try:
        # 1. Criar o Endereço primeiro
        address_data = data['Address']
        new_address = Address(
            Road=address_data.get('Road'),
            Neighbourhood=address_data.get('Neighbourhood'),
            Number=address_data.get('Number'),
            City=address_data.get('City'),
            State=address_data.get('State'),
            ZipCode=address_data.get('ZipCode'),
            Complement=address_data.get('Complement')
        )
        db.session.add(new_address)

        # Flush para gerar os dados de Address
        db.session.flush()

        # 2. Criar o Publisher
        new_publisher = Publisher(
            idAddress=new_address.idAddress, #Usar o ID do endereço gerado
            CNPJ=data.get('CNPJ'),
            Name=data.get('Name')
        )
        db.session.add(new_publisher)

        # 4. Se tudo certo, comitar a transação
        db.session.commit()

        return jsonify({'message': 'Publisher successfully created'}), 201

    except Exception as e:
        # 5. Se algo deu errado, reverter tudo
        db.session.rollback()
        logging.error(f"Failed to create publisher: {e}")
        return jsonify({"error": f"Failed to create publisher: {e}"}), 500