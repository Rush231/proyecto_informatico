from api.db.db_config import get_db_connection
import mysql.connector

class Cliente:
    def __init__(self, id, name, email, negocio_id=None):
        self.id = id
        self.name = name
        self.email = email
        self.negocio_id = negocio_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "negocio_id": self.negocio_id
        }
    
    @classmethod # <--- ESTO ES CRUCIAL PARA EVITAR EL ERROR DE 'datos'
    def validar(cls, datos):
        if not datos or not isinstance(datos, dict):
            return False, "Datos inválidos"
        if 'name' not in datos or not datos['name'].strip():
            return False, "El nombre es obligatorio"
        if 'email' not in datos or not datos['email'].strip():
            return False, "El email es obligatorio"
        return True, "OK"

    @classmethod
    def crear(cls, datos):
        # 1. Validar nombre y email
        valido, msg = cls.validar(datos)
        if not valido:
            return False, msg

        # 2. Obtener negocio_id (puede ser None)
        negocio_id = datos.get('negocio_id')

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 3. Insertar (negocio_id puede ser NULL en la BD)
            sql = "INSERT INTO Cliente (name, email, negocio_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datos['name'], datos['email'], negocio_id))
            conn.commit()
            
            return True, {"id": cursor.lastrowid, "mensaje": "Cliente creado exitosamente"}
        except mysql.connector.Error as err:
            return False, f"Error de Base de Datos: {err}"
        finally:
            if conn: conn.close()

    # ... (Manten tus otros métodos: obtener_por_negocio, obtener_todos, actualizar, eliminar) ...
    # Asegúrate de que todos tengan @classmethod si usan 'cls'
    @classmethod
    def obtener_todos_los_clientes(cls):
        # ... tu código existente ...
        pass # Rellena con tu código previo