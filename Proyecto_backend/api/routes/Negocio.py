from api import app
from flask import jsonify, request
from api.models.Negocio import Negocio
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.registro_servicios import RegistroService
from api.models.Profesional import Profesional

@app.route('/negocio/crear-negocio', methods=['POST'])
def crear_negocio():
    data = request.json
    conn = get_db_connection()
    
    if not conn: return jsonify({"error": "Error DB"}), 500

    try:
        cursor = conn.cursor()
        # Delegamos toda la lógica compleja al modelo/servicio
        resultado = RegistroService.crear_negocio_completo(cursor, data)
        
        conn.commit() # Confirmamos la transacción aquí
        
        return jsonify({
            "mensaje": "Negocio creado exitosamente",
            "datos": resultado
        }), 201

    except Exception as e:
        conn.rollback() # Si el servicio falla, deshacemos todo
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()



@app.route('/negocios', methods=['GET'])
def get_todos_negocios():
    try:
         lista = Negocio.get_todos_negocios()
         return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400
    

@app.route('/negocios/crear-con-dueno', methods=['POST'])
def crear_negocio_usuario_existente():
    """
    Crea un negocio y lo vincula a un usuario que YA existe.
    """
    datos = request.json
    # Esperamos: { "usuario_id": 25, "nombre_negocio": "Barberia", "tipo": "Estética" }
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # 1. Crear el Negocio
        nuevo_negocio = Negocio(datos['nombre_negocio'], datos['tipo'])
        negocio_id = nuevo_negocio.guardar(cursor)

        # 2. Vincular al usuario existente como DUEÑO
        # Usamos la clase Personal (o Profesional) para crear el vínculo
        nuevo_personal = Profesional(
            usuario_id=datos['usuario_id'], 
            negocio_id=negocio_id, 
            rol='dueno'
        )
        nuevo_personal.asignar_rol(cursor)

        conn.commit()
        return jsonify({
            "mensaje": "Negocio creado y vinculado", 
            "negocio_id": negocio_id
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn: conn.close()
