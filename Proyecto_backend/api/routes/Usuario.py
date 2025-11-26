from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.models.Usuario import Usuario
@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    datos = request.json
    
    # Datos del formulario
    nombre = datos['nombre']
    email = datos['email']
    contrasena = datos['contrasena']
    negocio_id = datos['negocio_id']


@app.route('/usuario/<int:id>', methods=['GET'])
def obtener_usuario(id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        usuario = Usuario.obtener_por_id(cursor, id)
        
        if usuario:
            return jsonify(usuario), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()

@app.route('/usuarios', methods=['GET'])
def get_todos_usuarios():
    try:
         lista = Usuario.get_todos_los_usuarios()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400