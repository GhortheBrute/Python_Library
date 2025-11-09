import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Book

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('routes', __name__, url_prefix='/api/clients')

@bp.route('/', methods=['POST'])
def create_book():
    """
    Endpoint for creating a client
    Awaits a JSON with client details and address
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação simples
    required_fields_fp = ['Email', 'Phone', 'Address', 'CPF', 'FName','LName', 'Birthdate']
    required_fields_jp = ['Email', 'Phone', 'Adress', 'CNPJ', 'Name']

    # Validação de dados Pessoa Física
    if data.get('Type') == 'PF':
        for field in required_fields_fp:
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

            # 2. Criar o Cliente pai
            new_client = Client(
                Type='PF',
                idAddress=new_address.idAddress, #Usar o ID do endereço gerado
                Phone=data.get('Phone'),
                Email=data.get('Email')
            )
            db.session.add(new_client)

            # Flush para ter o idClient
            db.session.flush()

            new_client_fp = ClientFP(
                idClient=new_client.idClient,
                CPF=data.get('CPF'),
                FName=data.get('FName'),
                MName=data.get('MName'),
                LName=data.get('LName'),
                Birthdate=data.get('Birthdate')
            )
            db.session.add(new_client_fp)

            # 4. Se tudo certo, comitar a transação
            db.session.commit()

            return jsonify({'message': 'Client successfully created'}), 201

        except Exception as e:
            # 5. Se algo deu errado, reverter tudo
            db.session.rollback()
            logging.error(f"Failed to create client: {e}")
            return jsonify({"error": f"Failed to create client"}), 500

    elif data.get('Type') == 'PJ':
        return jsonify({"message": "Featured not implemented."}), 501
    else:
        return jsonify({"error": "Client type must be 'PF'"}), 201