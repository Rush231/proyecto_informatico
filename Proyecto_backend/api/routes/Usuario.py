from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.models.Usuario import Usuario
import mysql.connector

@app.route('/usuario', methods=['POST'])
def crear_usuario():
    datos = request.json
    # Validación básica
    if not all(k in datos for k in ("nombre", "email", "contrasena", "negocio_id")):
        return jsonify({"error": "Faltan datos"}), 400

    sql = "INSERT INTO Usuario (name, email, password, negocio_id) VALUES (%s, %s, %s, %s)"
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (datos['nombre'], datos['email'], datos['contrasena'], datos['negocio_id']))
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