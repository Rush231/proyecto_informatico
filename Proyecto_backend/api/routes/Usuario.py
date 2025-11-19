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