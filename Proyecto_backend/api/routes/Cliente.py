from api import app
from flask import jsonify, request
from api.models.Cliente import Cliente
from api.db.db_config import get_db_connection
from api.db.db_config import mysql


@app.route('/clientes', methods=['GET'])
def get_todos_clientes():
    try:
         lista = Cliente.get_todos_clientes()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    

@app.route('/clientes/<int:id>', methods=['GET'])
def get_todos_clientes_por_id(id):
    try:
         lista = Cliente.get_todos_clientes_por_id()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    

@app.route('/cliente', methods=['POST'])
def crear_cliente():
    datos = request.json
    sql = "INSERT INTO Cliente (nombre, email) VALUES (%s, %s)"
    
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error de conexión"}), 500
            
        cursor = conn.cursor()
        cursor.execute(sql, (datos['nombre'], datos['email']))
        conn.commit()
        return jsonify({"mensaje": "Cliente creado", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()