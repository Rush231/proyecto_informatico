from api.db.db_config import get_db_connection
import mysql.connector

class Disponibilidad:
    def __init__(self, id, profesional_id, dia_semana, hora_inicio, hora_fin):
        self.id = id
        self.profesional_id = profesional_id
        self.dia_semana = dia_semana # 0=Lunes, 6=Domingo
        self.hora_inicio = hora_inicio # Formato "HH:MM:SS" o objeto time
        self.hora_fin = hora_fin

    def to_dict(self):
        # Convertimos objetos timedelta/time a string para que sea JSON serializable
        return {
            "id": self.id,
            "profesional_id": self.profesional_id,
            "dia_semana": self.dia_semana,
            "hora_inicio": str(self.hora_inicio), 
            "hora_fin": str(self.hora_fin)
        }

    @classmethod
    def crear(cls, datos):
        """
        Define el horario de un profesional para un día específico.
        """
        if not all(k in datos for k in ('profesional_id', 'dia_semana', 'hora_inicio', 'hora_fin')):
            return False, "Faltan datos"
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO Disponibilidad (profesional_id, dia_semana, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (datos['profesional_id'], datos['dia_semana'], datos['hora_inicio'], datos['hora_fin']))
            conn.commit()
            return True, {"id": cursor.lastrowid, "mensaje": "Disponibilidad creada"}
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if conn: conn.close()

    

    @classmethod
    def actualizar(cls, id, datos):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = "UPDATE Disponibilidad SET profesional_id=%s, dia_semana=%s, hora_inicio=%s, hora_fin=%s WHERE id=%s"
            cursor.execute(sql, (datos['profesional_id'], datos['dia_semana'], datos['hora_inicio'], datos['hora_fin'], id))
            conn.commit()
            if cursor.rowcount == 0:
                return False, "No se encontró la disponibilidad"
            return True, "Disponibilidad actualizada"
        except mysql.connector.Error as err:
            return False, f"Error BD: {err}"
        finally:
            if conn: conn.close()

    @classmethod
    def obtener_semanal(cls, profesional_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # Ordenamos por día de la semana
            cursor.execute("SELECT * FROM Disponibilidad WHERE profesional_id = %s ORDER BY dia_semana ASC", (profesional_id,))
            rows = cursor.fetchall()
            return [cls(**r).to_dict() for r in rows]
        finally:
            if 'conn' in locals() and conn: conn.close()