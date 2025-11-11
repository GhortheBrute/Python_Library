import logging

from flask import Blueprint, jsonify

from .. import db
from ..models import Reserve

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('reserves', __name__, url_prefix='/api/reserves')

@bp.route('/<int:client_id>/<string:isbn>/<int:branch_id>', methods=['POST'])
def create_reserve(client_id:int, isbn, branch_id:int):
    """
    Create a new reserve
    :param client_id: <int> Client ID
    :param isbn: <string> Book ISBN
    :param branch_id: <int> Branch ID
    """
    try:
        new_reserve = Reserve(
            ISBN=isbn,
            idBranch=branch_id,
            idClient=client_id
        )
        db.session.add(new_reserve)

        db.session.commit()
        return jsonify({'message': 'Reserve created!'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error on creating reserve: {e}")
        return jsonify({"message": f"Error on creating reserve: {e}"}), 500

@bp.route('/<int:reserve_id>', methods=['DELETE'])
def delete_reserve(reserve_id):
    """
    Delete a reserve
    :param reserve_id: <int> Reserve ID
    """
    try:
        result = db.session.query(Reserve).filter(Reserve.idReserve == reserve_id).first()

        if not result:
            return jsonify({'message': 'Reserve not found!'}), 404

        db.session.delete(result)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error on deleting reserve: {e}")
        return jsonify({'message': f"Error on deleting reserve: {e}"}), 500