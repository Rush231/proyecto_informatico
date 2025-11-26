# models/registro_service.py
from api.models.Usuario import Usuario
from api.models.Profesional import Profesional

class RegistroService:

    @staticmethod
    def agregar_personal(cursor, data):
        # --- 1. VALIDACIÓN CON TU CÓDIGO ---
        
        # Validamos parte del Usuario
        valido_user, mensaje_user = Usuario.validar(data)
        if not valido_user:
            raise ValueError(f"Error en datos de usuario: {mensaje_user}")

        # Validamos parte del Personal
        valido_pers, mensaje_pers = Profesional.validar(data)
        if not valido_pers:
            raise ValueError(f"Error en datos de personal: {mensaje_pers}")

        # --- 2. LÓGICA DE NEGOCIO (Si pasa la validación) ---
        
        # Crear Usuario
        nuevo_user = Usuario(data['nombre'], data['email'], data['contrasena'])
        user_id = nuevo_user.registrar(cursor)

        # Crear Personal
        rol = data.get('rol', 'profesional')
        especialidad = data.get('especialidad')
        
        nuevo_personal = Personal(user_id, data['negocio_id'], rol, especialidad)
        nuevo_personal.asignar_rol(cursor)

        return {"usuario_id": user_id, "rol": rol}