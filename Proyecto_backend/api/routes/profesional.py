from api import app
from flask import jsonify, request, g
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.Profesional import Profesional
from api.models.seguridad import token_required


# --- CREAR PROFESIONAL ---
@app.route('/profesional', methods=['POST'])
@token_required # <-- 3. Proteger la ruta
def crear_profesional():
    datos = request.json
    es_valido, mensaje = Profesional.validar(datos)
    if not es_valido:
        return jsonify({"error": mensaje}), 400
    try:
        # Inyectar el negocio_id desde el token por seguridad SaaS
        datos['negocio_id'] = g.negocio_id 
        nuevo = Profesional.crear(datos)
        return jsonify(nuevo), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- LISTAR PROFESIONALES ---
@app.route('/profesionales', methods=['GET']) # <-- 2. Agregar OPTIONS
@token_required # <-- 3. Proteger la ruta
def get_profesionales():
    try:
        # Ya no buscamos en la URL, sacamos el negocio_id seguro del token
        negocio_id = g.negocio_id
        
        if negocio_id:
            lista = Profesional.obtener_por_negocio(negocio_id)
        else:
            lista = Profesional.get_todos_los_profesionales()
            
        return jsonify(lista), 200
    except Exception as e:
         return jsonify({"error": str(e)}), 400

# --- TURNOS DEL PROFESIONAL ---
@app.route('/turnos/profesional/<int:profesional_id>', methods=['GET']) # <-- Agregar OPTIONS
@token_required
def get_turnos_profesional(profesional_id):
    turnos = Profesional.obtener_turnos(profesional_id)
    return jsonify(turnos), 200

# --- BORRAR PROFESIONAL ---
@app.route('/profesional/<int:id>', methods=['DELETE', 'OPTIONS']) # <-- Agregar OPTIONS
@token_required
def borrar_profesional(id):
    exito, res = Profesional.eliminar(id)
    return jsonify({"mensaje": res}), (200 if exito else 500)