from api import app
from flask import jsonify, request
from api.models.Disponibilidad import Disponibilidad
from api.db.db_config import get_db_connection
from api.db.db_config import mysql


@app.route('/disponibilidades', methods=['GET'])
def get_hay_disponibilidad():
    try:
         lista = Disponibilidad.get_hay_disponibilidad()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    



@app.route('/crear-disponibilidad', methods=['POST'])
def crear_disponibilidad():    
     try:
            datos = request.json
            nuevo = Disponibilidad.crear(datos)
            return jsonify(nuevo), 201
     except Exception as e:
            return jsonify({"error": str(e)}), 400
     

@app.route('/disponibilidad/actualizar/<int:id>', methods=['PUT'])
def actualizar_disponibilidad(id):
    try:
        datos = request.json
        actualizado = Disponibilidad.actualizar(id, datos)
        return jsonify(actualizado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400    
    

@app.route('/eliminar-disponibilidad/<int:id>', methods=['DELETE'])
def borrar_disponibilidad(id):
    try:
        exito, mensaje = Disponibilidad.eliminar(id)
        if exito:
            return jsonify({"mensaje": mensaje}), 200
        return jsonify({"error": mensaje}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400