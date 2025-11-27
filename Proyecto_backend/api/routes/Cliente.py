from api import app
from flask import jsonify, request
from api.models.Cliente import Cliente
from api.db.db_config import get_db_connection
from api.db.db_config import mysql


@app.route('/clientes', methods=['GET'])
def get_todos_clientes():
    try:
         lista = Cliente.obtener_todos_los_clientes()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    

@app.route('/clientes/<int:negocio_id>', methods=['GET'])
def get_todos_clientes_por_id(negocio_id):
    try:
         lista = Cliente.obtener_por_negocio(negocio_id)
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    

@app.route('/crear-cliente', methods=['POST'])
def crear_cliente():
    datos = request.json
    es_valido, mensaje = Cliente.validar(datos)
    if not es_valido:
        return jsonify({"error": mensaje}), 400
    conn = get_db_connection()
    try:
        nuevo = Cliente.crear(datos)
        return jsonify(nuevo), 201
    except Exception as e:
        return jsonify({"error": e.args[0]}), 500
    

@app.route('/cliente/<int:id>', methods=['PUT'])
def editar_cliente(id):
    datos = request.json
    exito, res = Cliente.actualizar(id, datos)
    if exito:
        return jsonify({"mensaje": res}), 200
    return jsonify({"error": res}), 400

# Eliminar Cliente (DELETE)
@app.route('/cliente/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    exito, res = Cliente.eliminar(id)
    if exito:
        return jsonify({"mensaje": res}), 200
    return jsonify({"error": res}), 500