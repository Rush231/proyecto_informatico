from api import app
from flask import jsonify, request
from api.models.Cliente import Cliente


@app.route('/usuario', methods=['POST'])
def crear_usuario():
    """Crea un nuevo usuario (dueño de negocio) con contraseña hasheada."""
    datos = request.json
    
    # Datos del formulario
    nombre = datos['nombre']
    email = datos['email']
    contrasena_plana = datos['contrasena'] # La contraseña del usuario
    negocio_id = datos['negocio_id']


@app.route('/usuario/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    """Obtiene los datos de un usuario por su ID."""
    usuario = Usuario.get_usuario_por_id(usuario_id)
    if usuario:
        return jsonify(usuario), 200
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404