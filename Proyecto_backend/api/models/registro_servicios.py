# models/registro_service.py
from api.models.Usuario import Usuario
from api.models.Profesional import Profesional
from api.models.Negocio import Negocio
class RegistroService:

    @classmethod
    def crear_negocio_completo(cls, cursor, datos):
        """
        Crea un Usuario, un Negocio y los vincula con el rol de 'dueno'.
        """
        
        # --- 1. VALIDACIÓN ---
        # Usamos el método validar que agregaste a tu modelo Usuario
        es_valido, mensaje = Usuario.validar(datos)
        if not es_valido:
            raise ValueError(f"Error en datos de usuario: {mensaje}")
            
        # Validación manual simple para el negocio (o usa Negocio.validar si lo creaste)
        if 'nombre_negocio' not in datos or not datos['nombre_negocio']:
            raise ValueError("Falta el nombre_negocio")
        if 'tipo_negocio' not in datos or not datos['tipo_negocio']:
            raise ValueError("Falta el tipo_negocio")

        # --- 2. CREAR USUARIO (Identidad) ---
        # Instanciamos y guardamos. 
        # Nota: Pasamos None en negocio_id porque en la nueva lógica se vincula después
        nuevo_usuario = Usuario(datos['name'], datos['email'], datos['password'])
        usuario_id = nuevo_usuario.registrar(cursor)

        # --- 3. CREAR NEGOCIO ---
        nuevo_negocio = Negocio(datos['nombre_negocio'], datos['tipo_negocio'])
        negocio_id = nuevo_negocio.guardar(cursor)

        # --- 4. VINCULAR (Crear el Personal/Dueño) ---
        # Aquí asignamos el rol 'dueno'
        nuevo_personal = Profesional(usuario_id, negocio_id, 'dueno')
        nuevo_personal.asignar_rol(cursor)

        return {
            "usuario_id": usuario_id,
            "negocio_id": negocio_id,
            "mensaje": "Negocio registrado exitosamente"
        }



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
        
        nuevo_personal = Profesional(user_id, data['negocio_id'], rol, especialidad)
        nuevo_personal.asignar_rol(cursor)

        return {"usuario_id": user_id, "rol": rol}