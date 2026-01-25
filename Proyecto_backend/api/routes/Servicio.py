from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.Servicio import Servicio
from api.models.seguridad import token_required

@app.route('/servicio', methods=['POST'])
@token_required
def crear_servicio():
    datos = request.json
    resultado, respuesta = Servicio.crear(datos)
    if resultado:
        return jsonify(respuesta), 201
    else:
        return jsonify({"error": respuesta}), 400

@app.route('/servicios/<int:negocio_id>', methods=['GET'])
@token_required
def listar_servicios(current_user):
    negocio_id = current_user['negocio_id']
    lista = Servicio.obtener_por_negocio(negocio_id)
    return jsonify(lista), 200


@app.route('/servicio/<int:id>', methods=['DELETE'])
@token_required
def borrar_servicio(current_user, id):
    negocio_id = current_user['negocio_id']
    exito, mensaje = Servicio.eliminar(id,negocio_id)
    if exito:
        return jsonify({"mensaje": mensaje}), 200
    return jsonify({"error": mensaje}), 400

@app.route('/servicios', methods =['GET'])
def get_servicios():
    try:
         lista = Servicio.obtener_todos()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    

@app.route('/servicio/<int:id>', methods=['PUT'])
def actualizar_servicio(id):
    datos = request.json
    exito, mensaje = Servicio.actualizar(id, datos)
    if exito:
        return jsonify({"mensaje": mensaje}), 200
    return jsonify({"error": mensaje}), 400