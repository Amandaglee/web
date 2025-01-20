from flask import Blueprint, jsonify


bp = Blueprint('test', __name__, url_prefix='/')


@bp.route('/user', methods=['GET'])
def hello_world():
    return jsonify({'message': 'Hello World!'})