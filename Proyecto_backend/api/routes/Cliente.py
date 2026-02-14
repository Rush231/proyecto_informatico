from api import app
from flask import jsonify, request, g
from api.models.Cliente import Cliente
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.seguridad import token_required

# 1. Agregamos OPTIONS a los métodos permitidos
@app.route('/clientes', methods=['GET']) 
def get_todos_clientes():
    try:
         # 3. MAGIA SAAS: Ya no usamos request.args.get('negocio_id')
         # Ahora lo leemos directamente desde el Token (g.negocio_id)
         negocio_id = g.negocio_id 
         
         if not negocio_id:
            return jsonify({"error": "Usuario sin negocio asignado"}), 400
         
         lista = Cliente.obtener_por_negocio(negocio_id)
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
    

@app.route('/clientes', methods=['POST']) # Nota: corregí la ruta de '/crear' a '/clientes' para seguir REST
@token_required
def crear_cliente(current_user):
    datos = request.json
    
    # 4. FORZAMOS EL NEGOCIO ID DEL TOKEN
    # Aunque el frontend mande otro ID, nosotros lo sobrescribimos aquí.
    datos['negocio_id'] = current_user['negocio_id'] 

    es_valido, mensaje = Cliente.validar(datos)
    if not es_valido:
        return jsonify({"error": mensaje}), 400
    
    try:
        exito, resultado = Cliente.crear(datos)
        if exito:
            return jsonify(resultado), 201
        else:
            return jsonify({"error": resultado}), 500     
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clientes/<int:id>', methods=['PUT'])
def editar_cliente(current_user, id):
    datos = request.json
    exito, res = Cliente.actualizar(id, datos, current_user['negocio_id'])
    if exito:
        return jsonify({"mensaje": res}), 200
    return jsonify({"error": res}), 400

# Eliminar Cliente (DELETE)
@app.route('/cliente/<int:id>', methods=['DELETE'])
@token_required
def eliminar_cliente(current_user, id):
    exito, res = Cliente.eliminar(id, current_user['negocio_id'])
    if exito:
        return jsonify({"mensaje": res}), 200
    return jsonify({"error": res}), 500