from api import app
from flask import jsonify, request
from api.db.db_config import get_db_connection
from api.db.db_config import mysql
from api.models.Turno import Turno
from api.models.Servicio import Servicio
@app.route('/crear-turno', methods=['POST'])
def crear_turno():
    datos = request.json

    resultado, respuesta = Turno.crear(datos)

    if resultado:
        return jsonify(respuesta), 201
    else:
        status_code = 409 if "disponible" in str(respuesta) else 400
        return jsonify({"error": respuesta}), status_code
    

@app.route('/turnos/cliente/<int:cliente_id>', methods=['GET'])
def listar_turnos_cliente(cliente_id):
    turnos = Turno.obtener_por_cliente(cliente_id)
    return jsonify(turnos), 200


from api.models.Servicio import Servicio  

@app.route('/turnos/disponibles', methods=['GET'])
def obtener_horarios_disponibles():
    # 1. Recibir datos
    profesional_id = request.args.get('profesional_id')
    fecha = request.args.get('fecha')
    servicio_id = request.args.get('servicio_id')

    if not all([profesional_id, fecha, servicio_id]):
        return jsonify({"error": "Faltan parámetros"}), 400

    try:
        #  Pedir al MODELO la información del servicio
        servicio = Servicio.obtener_por_id(servicio_id)
        
        if not servicio:
            return jsonify({"error": "Servicio no encontrado"}), 404

        # Pedir al MODELO Turno que calcule los horarios
    
        horarios = Turno.buscar_horarios_disponibles(
            profesional_id, 
            fecha, 
            servicio['duracion']
        )
        
        return jsonify(horarios), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route('/turnos/negocio/<int:negocio_id>', methods=['GET'])
def listar_turnos_negocio(negocio_id):
    turnos = Turno.obtener_por_negocio(negocio_id)
    return jsonify(turnos), 200