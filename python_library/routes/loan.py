import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Book, Publisher, Author, Collection

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('loans', __name__, url_prefix='/api/loans')