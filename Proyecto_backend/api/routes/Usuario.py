from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.models.Usuario import Usuario
import mysql.connector

@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    datos = request.json
    
    
    # SQL corregido para coincidir con tus columnas de DB (name, password)
    sql = "INSERT INTO Usuario (name, email, password, negocio_id) VALUES (%s, %s, %s, %s)"
    
    # ... resto del código con execute(sql, (name, email, password, negocio_id)) ...
    # Validación básica
    if not all(k in datos for k in ("name", "email", "password", "negocio_id")):
        return jsonify({"error": "Faltan datos"}), 400

    sql = "INSERT INTO Usuario (name, email, password, negocio_id) VALUES (%s, %s, %s, %s)"
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (datos['name'], datos['email'], datos['password'], datos['negocio_id']))
        conn.commit()
        return jsonify({"mensaje": "Usuario creado", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

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