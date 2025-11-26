from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql



@app.route('/turno', methods=['POST'])
def crear_turno():
    """Crea un nuevo turno (la reserva)."""
    datos = request.json
    # Se esperan: cliente_id, profesional_id, servicio_id, fecha_hora
    sql = "INSERT INTO Turno (cliente_id, profesional_id, servicio_id, fecha_hora, estado) VALUES (%s, %s, %s, %s, 'reservado')"
    
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error de conexión"}), 500

        # ---
        # NOTA IMPORTANTE: Aca faltaría la validación de disponibilidad.
        # verificar que:
        # 1. La 'fecha_hora' esté dentro de la 'Disponibilidad' del profesional.
        # 2. No se superponga con otro 'Turno' existente para ese profesional.
        # ---
        
        cursor = conn.cursor()
        cursor.execute(sql, (datos['cliente_id'], datos['profesional_id'], datos['servicio_id'], datos['fecha_hora']))
        conn.commit()
        return jsonify({"mensaje": "Turno creado exitosamente", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()
