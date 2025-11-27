from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.models.Usuario import Usuario
import mysql.connector

@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    datos = request.json

    es_valido, mensaje = Usuario.validar(datos)
    if not es_valido:
        return jsonify({"error": mensaje}), 400
    conn = get_db_connection()
    try:
        nuevo = Usuario.registrar(datos)
        return jsonify(nuevo), 201
    except Exception as e:
        return jsonify({"error": e.args[0]}), 500

# --- Ruta para OBTENER Usuarios (Opcional, si la necesitas) ---
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    Usuario.get_todos_los_usuarios() 
    try:
         lista = Usuario.get_todos_los_usuarios()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    

@app.route('/usuario/<int:id>', methods=['GET'])
def get_usuario(id):
    try:
         usuario = Usuario.usuario_por_id(id)
         if usuario:
             return jsonify(usuario), 200
         else:
             return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
         return jsonify({"error": str(e)}), 400