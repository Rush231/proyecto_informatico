from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.Turno import Turno

@app.route('/crear-turno', methods=['POST'])
def crear_turno():
    datos = request.json

    resultado, respuesta = Turno.crear(datos)

    if resultado:
        return jsonify(respuesta), 201
    else:
        status_code = 409 if "disponible" in str(respuesta) else 400
        return jsonify({"error": respuesta}), status_code
    

@app.route('/turnos/cliente/<int:cliente_id>', methods=['GET'])
def listar_turnos_cliente(cliente_id):
    turnos = Turno.obtener_por_cliente(cliente_id)
    return jsonify(turnos), 200