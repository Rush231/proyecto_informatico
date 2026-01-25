from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.Profesional import Profesional
from api.models.seguridad import token_required
@app.route('/profesional', methods=['POST'])
@token_required
def crear_profesional(current_user):
    datos = request.json
    
    # Inyectamos el negocio del dueño
    datos['negocio_id'] = current_user['negocio_id']

    es_valido, mensaje = Profesional.validar(datos)
    if not es_valido:
        return jsonify({"error": mensaje}), 400
        
    try:
        exito, resultado = Profesional.crear(datos)
        if exito:
            return jsonify(resultado), 201
        return jsonify({"error": resultado}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/profesionales', methods=['GET'])
@token_required
def get_mis_profesionales(current_user):
    # Obtenemos solo los de mi negocio
    negocio_id = current_user['negocio_id']
    try:
        lista = Profesional.obtener_por_negocio(negocio_id)
        return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400

@app.route('/profesional/<int:id>', methods=['DELETE'])
@token_required
def borrar_profesional(current_user, id):
    negocio_id = current_user['negocio_id']
    
    exito, res = Profesional.eliminar(id, negocio_id)
    
    if exito:
        return jsonify({"mensaje": res}), 200
    return jsonify({"error": res}), 403