from api import app
from flask import jsonify, request
from api.models.Negocio import Negocio
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.registro_servicios import RegistroService
from api.models.Profesional import Profesional

@app.route('/negocio/crear-negocio', methods=['POST'])
def crear_negocio():
    data = request.json
    conn = get_db_connection()
    
    exito, respuesta = Negocio.crear(data)
    
    if exito:
        return jsonify(respuesta), 201
    else:
        return jsonify({"error": respuesta}), 400



@app.route('/negocios', methods=['GET'])
def get_todos_negocios():
    try:
         lista = Negocio.get_todos_negocios()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    


@app.route('/negocio/borrar/<int:id>', methods=['DELETE'])
def borrar_negocio(id):
    exito, res = Negocio.borrar_negocio(id)
    return jsonify({"mensaje": res}), (200 if exito else 500)

@app.route('/negocio/<int:id>', methods=['GET'])
def obtener_negocio(id):
    negocio = Negocio.obtener_por_id(id)
    if negocio:
        return jsonify(negocio), 200
    else:
        return jsonify({"error": "Negocio no encontrado"}), 404