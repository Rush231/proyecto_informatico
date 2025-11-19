from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql

@app.route('/servicio', methods=['POST'])
def crear_servicio():
    datos = request.json
    sql = "INSERT INTO Servicio (nombre, duracion, negocio_id) VALUES (%s, %s, %s)"
    
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error de conexión"}), 500
            
        cursor = conn.cursor()
        cursor.execute(sql, (datos['nombre'], datos['duracion'], datos['negocio_id']))
        conn.commit()
        return jsonify({"mensaje": "Servicio creado", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()