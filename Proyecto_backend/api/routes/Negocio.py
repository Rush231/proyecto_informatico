from api import app
from flask import jsonify, request
from api.models.Negocio import Negocio
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.registro_servicios import RegistroService

@app.route('/negocios/crear-negocio', methods=['POST'])
def crear_negocio_completo():
    data = request.json
    conn = get_db_connection()
    
    if not conn: return jsonify({"error": "Error DB"}), 500

    try:
        cursor = conn.cursor()
        # Delegamos toda la lógica compleja al modelo/servicio
        resultado = RegistroService.registrar_negocio_completo(cursor, data)
        
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
    


