import logging

from flask import Blueprint, request, jsonify

from . import db
from .models import Address, Client, ClientFP, ClientJP

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('routes', __name__)

@bp.route('/')
def hello_world():
    return 'Olá mundo!'

@bp.route('/api/clients', methods=['POST'])
def create_client():
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

@bp.route('/api/clients', methods=['GET'])
def get_clients():
    """
    Endpoint for getting all clients
    """
    try:
        # 1. Fazemos a consulta unindo as 4 tabelas de Clientes
        # (Client, ClientFP, ClientJP, Address)
        results = db.session.query(
            Client,
            ClientFP,
            ClientJP,
            Address
        ).join(
            Address, Client.idAddress == Address.idAddress
        ).outerjoin(
            ClientJP, Client.idClient == ClientJP.idClient
        ).outerjoin(
            ClientFP, Client.idClient == ClientFP.idClient
        ).all() # .all() para pegar todos

        # 2. Formatamos os resultados para JSON
        output= []
        for client, client_fp, client_jp, address in results:
            # Foco em Pessoas Físicas por enquanto
            if client.Type=='PF':
                client_data = {
                    'idClient': client.idClient,
                    'Type': client.Type,
                    'CPF': client_fp.CPF,
                    'Name': f"{client_fp.FName} {client_fp.MName} {client_fp.LName}",
                    'Birthdate': client_fp.Birthdate.isoformat() if client_fp.Birthdate else None,
                    'Phone': client.Phone,
                    'Email': client.Email,
                    'Address': {
                        'Road': address.Road,
                        'Neighbourhood': address.Neighbourhood,
                        'Number': address.Number,
                        'City': address.City,
                        'State': address.State,
                        'ZipCode': address.ZipCode,
                        'Complement': address.Complement
                    }
                }
                output.append(client_data)

            # Para Pessoa Jurídica
            elif client.Type=='PJ':
                client_data = {
                    'idClient': client.idClient,
                    'Type': client.Type,
                    'CNPJ': client_jp.CPF,
                    'Name': client_jp.Name,
                    'FantasyName': client_jp.FantasyName,
                    'Phone': client.Phone,
                    'Email': client.Email,
                    'Address': {
                        'Road': address.Road,
                        'Neighbourhood': address.Neighbourhood,
                        'Number': address.Number,
                        'City': address.City,
                        'State': address.State,
                        'ZipCode': address.ZipCode,
                        'Complement': address.Complement
                    }
                }
                output.append(client_data)

        return jsonify({'clients': output}), 200

    except Exception as e:
        logging.error(f"Failed to get clients: {e}")
        return jsonify({"error": f"Failed to get clients"}), 500

@bp.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """
    Endpoint for getting a specific client by ID
    """
    client_data = {}
    try:
        # 1. Fazemos a mesma consulta, mas filtramos pelo ID
        result = db.session.query(
            Client,
            ClientFP,
            ClientJP,
            Address
        ).join(
            Address, Client.idAddress == Address.idAddress
        ).outerjoin(
            ClientJP, Client.idClient == ClientJP.idClient
        ).outerjoin(
            ClientFP, Client.idClient == ClientFP.idClient
        ).filter(
            Client.idClient == client_id
        ).first() # .first() pega apenas um

        # 2. Verificamos se o cliente foi encontrado
        if not result:
            return jsonify({"error": "Client not found"}), 404

        # 3. Desempacotamos os resultados
        client, client_fp, client_jp, address = result

        # 4. Formatamos o JSON de resposta
        # Para PF
        if client.Type=='PF':
            client_data = {
                'idClient': client.idClient,
                'Type': client.Type,
                'CPF': client_fp.CPF,
                'FName': client_fp.FName,
                'MName': client_fp.MName,
                'LName': client_fp.LName,
                'Birthdate': client_fp.Birthdate.isoformat() if client_fp.Birthdate else None,
                'Phone': client.Phone,
                'Email': client.Email,
                'Address': {
                    'Road': address.Road,
                    'Neighbourhood': address.Neighbourhood,
                    'Number': address.Number,
                    'City': address.City,
                    'State': address.State,
                    'ZipCode': address.ZipCode,
                    'Complement': address.Complement
                }
            }
            return jsonify(client_data), 200

        elif client.Type == 'PJ':
            client_data = {
                'idClient': client.idClient,
                'Type': client.Type,
                'CNPJ': client_jp.CPF,
                'Name': client_jp.Name,
                'FantasyName': client_jp.FantasyName,
                'Phone': client.Phone,
                'Email': client.Email,
                'Address': {
                    'Road': address.Road,
                    'Neighbourhood': address.Neighbourhood,
                    'Number': address.Number,
                    'City': address.City,
                    'State': address.State,
                    'ZipCode': address.ZipCode,
                    'Complement': address.Complement
                }
            }
            return jsonify(client_data), 200

        else:
            return jsonify({"error": "Client not found"}), 404

    except Exception as e:
        logging.error(f"Failed to get client: {e}")
        return jsonify({"error": f"Failed to get client: {e}"}), 500