from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql



@app.route('/profesional', methods=['POST'])
def crear_profesional():
    datos = request.json
    sql = "INSERT INTO Profesional (nombre, especialidad, negocio_id) VALUES (%s, %s, %s)"
    
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error de conexión"}), 500
            
        cursor = conn.cursor()
        cursor.execute(sql, (datos['nombre'], datos.get('especialidad'), datos['negocio_id']))
        conn.commit()
        return jsonify({"mensaje": "Profesional creado", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()