from api.db.db_config import get_db_connection
import mysql.connector

class Servicio:
    def __init__(self, id, name, duracion, negocio_id):
        self.id = id
        self.name = name
        self.duracion = duracion
        self.negocio_id = negocio_id

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.name,
            "duracion": self.duracion,
            "negocio_id": self.negocio_id
        }

    @classmethod
    def crear(cls, datos):
        if 'nombre' not in datos or 'duracion' not in datos or 'negocio_id' not in datos:
            return False, "Faltan datos obligatorios (nombre, duracion, negocio_id)"

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO Servicio (name, duracion, negocio_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datos['nombre'], datos['duracion'], datos['negocio_id']))
            conn.commit()
            return True, {"id": cursor.lastrowid, "mensaje": "Servicio creado"}
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if 'conn' in locals() and conn: conn.close()

    @classmethod
    def obtener_por_negocio(cls, negocio_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Servicio WHERE negocio_id = %s", (negocio_id,))
            rows = cursor.fetchall()
            return [cls(r['id'], r['name'], r['duracion'], r['negocio_id']).to_dict() for r in rows]
        except mysql.connector.Error:
            return []
        finally:
            if 'conn' in locals() and conn: conn.close()