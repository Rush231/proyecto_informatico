from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.Turno import Turno


@app.route('/turno', methods=['POST'])
def crear_turno():
    datos = request.json
    # Datos esperados: cliente_id, profesional_id, servicio_id, fecha_hora
    
    # --- VALIDACIÓN EN EL MODELO (Limpio) ---
    es_valido, mensaje_error = Turno.es_horario_valido(
        datos['profesional_id'], 
        datos['servicio_id'], 
        datos['fecha_hora']
    )

    if not es_valido:
        return jsonify({"error": mensaje_error}), 409 # 409 Conflict
    # ----------------------------------------

    # Si pasa, guardamos
    sql = "INSERT INTO Turno (cliente_id, profesional_id, servicio_id, fecha_hora, estado) VALUES (%s, %s, %s, %s, 'reservado')"
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (datos['cliente_id'], datos['profesional_id'], datos['servicio_id'], datos['fecha_hora']))
        conn.commit()
        return jsonify({"mensaje": "Turno creado exitosamente", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if conn:
            conn.close()