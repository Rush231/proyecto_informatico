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
    @classmethod
    def validar(cls, datos):
        if not datos or not isinstance(datos, dict):
            return False, "Datos inválidos"
        if 'name' not in datos or not datos['name'].strip():
            return False, "El nombre es obligatorio"
        if 'email' not in datos or not datos['email'].strip():
            return False, "El email es obligatorio"
        # NO validamos negocio_id aquí, para que sea opcional
        return True, "OK"

    @classmethod
    def crear(cls, datos):
        # Validamos lo básico
        if 'name' not in datos or 'email' not in datos:
            return False, "Nombre y Email son obligatorios"
            
        # Obtenemos el negocio_id. Si no viene, será None (NULL en la BD)
        negocio_id = datos.get('negocio_id') 

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insertamos. Si negocio_id es None, se guardará como NULL
            sql = "INSERT INTO Cliente (name, email, negocio_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datos['name'], datos['email'], negocio_id))
            conn.commit()
            return True, {"id": cursor.lastrowid, "mensaje": "Cliente registrado exitosamente"}
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if 'conn' in locals() and conn:
                conn.close()

    @classmethod
    def obtener_por_negocio(cls, negocio_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM Cliente WHERE negocio_id = %s"
            cursor.execute(sql, (negocio_id,))
            rows = cursor.fetchall()
            return [cls(r['id'], r['name'], r['email'], r['negocio_id']).to_dict() for r in rows]
        except mysql.connector.Error:
            return []
        finally:
            if 'conn' in locals() and conn: conn.close()

    @classmethod
    def obtener_todos_los_clientes(cls):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM Cliente"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [cls(r['id'], r['name'], r['email'], r['negocio_id']).to_dict() for r in rows]
        except mysql.connector.Error:
            return []
        finally:
            if 'conn' in locals() and conn: conn.close()

    @classmethod
    def actualizar(cls, id, datos):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = "UPDATE Cliente SET name=%s, email=%s WHERE id=%s"
            cursor.execute(sql, (datos['nombre'], datos['email'], id))
            conn.commit()
            return True, "Cliente actualizado"
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if 'conn' in locals() and conn: conn.close()

    @classmethod
    def eliminar(cls, id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Cliente WHERE id = %s", (id,))
            conn.commit()
            return True, "Cliente eliminado"
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if 'conn' in locals() and conn: conn.close()