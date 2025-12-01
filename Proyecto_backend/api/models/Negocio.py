from api.db.db_config import get_db_connection
import mysql.connector

class Negocio:
    def __init__(self, id, name, tipo):
        self.id = id
        self.name = name
        self.tipo = tipo

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tipo": self.tipo
        }

    @classmethod
    def crear(cls, datos):
        if 'name' not in datos:
            return False, "El nombre del negocio es obligatorio"

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = "INSERT INTO Negocio (name, tipo) VALUES (%s, %s)"
            # Usamos .get() para 'tipo' porque en tu SQL no es obligatorio (puede ser NULL)
            cursor.execute(sql, (datos['name'], datos.get('tipo')))
            conn.commit()
            
            return True, {"id": cursor.lastrowid, "mensaje": "Negocio creado exitosamente"}
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if conn: conn.close()

    @classmethod
    def obtener_por_id(cls, id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Negocio WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                return cls(row['id'], row['name'], row['tipo']).to_dict()
            return None
        finally:
            if 'conn' in locals() and conn: conn.close()


    @classmethod
    def borrar_negocio(cls, id):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Negocio WHERE id = %s", (id,))
            conn.commit()
            if cursor.rowcount == 0:
                return False, "Negocio no encontrado"
            return True, "Negocio borrado exitosamente"
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if conn: conn.close()


    @classmethod
    def get_todos_negocios(cls):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Negocio")
            rows = cursor.fetchall()
            negocios = [cls(row['id'], row['name'], row['tipo']).to_dict() for row in rows]
            return negocios
        finally:
            if conn: conn.close()