from api.db.db_config import get_db_connection
import mysql.connector


class Profesional:
    def __init__(self, id, name, especialidad, negocio_id, email=None):
        self.id = id
        self.name = name
        self.especialidad = especialidad
        self.negocio_id = negocio_id
        self.email = email

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "especialidad": self.especialidad,
            "negocio_id": self.negocio_id,
            "email": self.email
        }

    @classmethod
    def validar(cls, datos):
        if not datos or not isinstance(datos, dict):
            return False, "Datos inválidos"
        if 'name' not in datos or not datos['name'].strip():
            return False, "El nombre es obligatorio"
        if 'negocio_id' not in datos:
            return False, "El ID del negocio es obligatorio"
        return True, "OK"

    @classmethod
    def crear(cls, datos):
        valido, msg = cls.validar(datos)
        if not valido: return False, msg

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Asegúrate que las columnas en tu BD sean correctas
            sql = "INSERT INTO Profesional (name, especialidad, negocio_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datos['name'], datos.get('especialidad', ''), datos['negocio_id']))
            conn.commit()
            return True, {"id": cursor.lastrowid, "mensaje": "Profesional creado"}
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if 'conn' in locals() and conn: conn.close()

    @classmethod
    def obtener_por_negocio(cls, negocio_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM Profesional WHERE negocio_id = %s"
            cursor.execute(sql, (negocio_id,))
            rows = cursor.fetchall()
            return [cls(r['id'], r['name'], r['especialidad'], r['negocio_id']).to_dict() for r in rows]
        except mysql.connector.Error:
            return []
        finally:
            if 'conn' in locals() and conn: conn.close()

    @classmethod
    def eliminar(cls, id, negocio_id):
        # CAMBIO: Seguridad con negocio_id
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM Profesional WHERE id = %s AND negocio_id = %s"
            cursor.execute(sql, (id, negocio_id))
            conn.commit()
            
            if cursor.rowcount == 0:
                return False, "No se pudo eliminar (No encontrado o permiso denegado)"
                
            return True, "Profesional eliminado"
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if 'conn' in locals() and conn: conn.close()


    @classmethod
    def get_todos_los_profesionales(cls):
        # CORRECTO: Dejamos "name" tal cual
        query = "SELECT id, name, negocio_id FROM Profesional"
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados
        except mysql.connector.Error as err:
            print(f"Error en get_todos_los_profesionales: {err}")
            return []
        finally:
            if conn:
                conn.close()

