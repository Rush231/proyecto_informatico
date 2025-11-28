from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.Profesional import Profesional
@app.route('/crear-profesional', methods=['POST'])
def crear_profesional():
    datos = request.json

    es_valido, mensaje = Profesional.validar(datos)
    if not es_valido:
        return jsonify({"error": mensaje}), 400
    conn = get_db_connection()
    try:
        nuevo = Profesional.crear(datos)
        return jsonify(nuevo), 201
    except Exception as e:
        return jsonify({"error": e.args[0]}), 500


@app.route('/profesionales/<int:negocio_id>', methods=['GET'])
def listar_profesionales(negocio_id):
    lista = Profesional.obtener_por_negocio(negocio_id)
    return jsonify(lista), 200


@app.route('/profesionales', methods=['GET'])
def get_profesionales():
    try:
         lista = Profesional.get_todos_los_profesionales()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400

@app.route('/turnos/profesional/<int:profesional_id>', methods=['GET'])
def get_turnos_profesional(profesional_id):
    turnos = Profesional.obtener_turnos(profesional_id)
    return jsonify(turnos), 200

@app.route('/profesional/<int:id>', methods=['DELETE'])
def borrar_profesional(id):
    exito, res = Profesional.eliminar(id)
    return jsonify({"mensaje": res}), (200 if exito else 500)