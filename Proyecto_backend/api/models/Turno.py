from datetime import datetime, timedelta, date
from api.db.db_config import get_db_connection
import mysql.connector
class Turno:
    def __init__(self, cliente_id, profesional_id, servicio_id, fecha_hora, estado='reservado', id=None):
        self.id = id
        self.cliente_id = cliente_id
        self.profesional_id = profesional_id
        self.servicio_id = servicio_id
        self.fecha_hora = fecha_hora
        self.estado = estado

    @classmethod
    def buscar_horarios_disponibles(cls, profesional_id, fecha_str, duracion_minutos):
        """
        Genera los horarios disponibles para un profesional en una fecha específica.
        fecha_str: 'YYYY-MM-DD'
        duracion_minutos: int (duración del servicio)
        """
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        #Identificar qué día de la semana es (0=Lunes, 6=Domingo)
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        dia_semana = fecha_obj.weekday()

        try:
            # Obtener la regla general de disponibilidad para ese día
            sql_disp = "SELECT hora_inicio, hora_fin FROM Disponibilidad WHERE profesional_id = %s AND dia_semana = %s"
            cursor.execute(sql_disp, (profesional_id, dia_semana))
            regla = cursor.fetchone()

            if not regla:
                return [] # El profesional no trabaja ese día

            # Convertir a objetos datetime completos para comparar
            inicio_jornada = datetime.combine(fecha_obj, (timedelta(seconds=regla['hora_inicio'].total_seconds())).to_pytime()) if isinstance(regla['hora_inicio'], timedelta) else datetime.combine(fecha_obj, datetime.strptime(str(regla['hora_inicio']), "%H:%M:%S").time())
            fin_jornada = datetime.combine(fecha_obj, (timedelta(seconds=regla['hora_fin'].total_seconds())).to_pytime()) if isinstance(regla['hora_fin'], timedelta) else datetime.combine(fecha_obj, datetime.strptime(str(regla['hora_fin']), "%H:%M:%S").time())

            #  TURNOS YA OCUPADOS ese día
            sql_turnos = "SELECT fecha_hora FROM Turno WHERE profesional_id = %s AND DATE(fecha_hora) = %s AND estado != 'cancelado'"
            cursor.execute(sql_turnos, (profesional_id, fecha_str))
            ocupados = [row['fecha_hora'] for row in cursor.fetchall()]

            # BLOQUEOS (Excepciones/Feriados)
            # Buscamos bloqueos que se solapen con este día
            sql_bloqueos = """
                SELECT fecha_inicio, fecha_fin FROM BloqueoAgenda 
                WHERE profesional_id = %s 
                AND (DATE(fecha_inicio) <= %s AND DATE(fecha_fin) >= %s)
            """
            cursor.execute(sql_bloqueos, (profesional_id, fecha_str, fecha_str))
            bloqueos = cursor.fetchall()

            # Algoritmo de Barrido (Generación de Slots)
            horarios_disponibles = []
            tiempo_actual = inicio_jornada
            
            while tiempo_actual + timedelta(minutes=duracion_minutos) <= fin_jornada:
                tiempo_fin_turno = tiempo_actual + timedelta(minutes=duracion_minutos)
                esta_libre = True

                # A. Verificar colisión con Turnos existentes
                for ocupado in ocupados:
                    if ocupado == tiempo_actual: 
                        esta_libre = False
                        break

                # B. Verificar colisión con Bloqueos/Excepciones
                if esta_libre:
                    for bloque in bloqueos:
                        b_inicio = bloque['fecha_inicio']
                        b_fin = bloque['fecha_fin']
                        # Lógica de solapamiento de rangos
                        if (tiempo_actual < b_fin) and (tiempo_fin_turno > b_inicio):
                            esta_libre = False
                            break
                
                if esta_libre:
                    horarios_disponibles.append(tiempo_actual.strftime('%H:%M'))
                
        
                tiempo_actual += timedelta(minutes=duracion_minutos)

            return horarios_disponibles

        finally:
            conn.close()

    @classmethod
    def es_horario_valido(cls, profesional_id, servicio_id, fecha_hora_str):
        """
        Verifica si se puede agendar un turno en esa fecha y hora.
        Retorna: (Booleano, Mensaje)
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # 1. Obtener la duración del servicio internamente
            cursor.execute("SELECT duracion FROM Servicio WHERE id = %s", (servicio_id,))
            servicio = cursor.fetchone()
            
            if not servicio:
                return False, "El servicio especificado no existe."
            
            duracion = servicio['duracion']

            # 2. Preparar datos para la búsqueda
            # fecha_hora_str viene como "2023-11-20 10:00:00"
            try:
                fecha_obj = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
                fecha_solo_str = fecha_obj.strftime('%Y-%m-%d')
                hora_solicitada = fecha_obj.strftime('%H:%M')
            except ValueError:
                return False, "Formato de fecha inválido. Use AAAA-MM-DD HH:MM:SS"

            # 3. Reutilizamos la lógica de buscar disponibles (el método que hicimos antes)
            horarios_disponibles = cls.buscar_horarios_disponibles(profesional_id, fecha_solo_str, duracion)

            # 4. Validar
            if hora_solicitada in horarios_disponibles:
                return True, "Horario disponible"
            else:
                return False, "El horario seleccionado no está disponible (ocupado, feriado o fuera de rango)."

        except Exception as e:
            return False, f"Error interno al validar: {str(e)}"
        finally:
            if conn: conn.close()
    @classmethod
    def crear(cls, datos):
        """
        Orquesta la creación del turno: Valida -> Conecta -> Guarda
        Retorna: (Exito: bool, Resultado: dict/str)
        """
        # 1. Extraer datos
        cliente_id = datos.get('cliente_id')
        profesional_id = datos.get('profesional_id')
        servicio_id = datos.get('servicio_id')
        fecha_hora = datos.get('fecha_hora')

        # 2. Validar reglas de negocio (Horarios, bloqueos, etc.)
        es_valido, mensaje = cls.es_horario_valido(profesional_id, servicio_id, fecha_hora)
        if not es_valido:
            return False, mensaje # Retornamos el error de validación

        # 3. Guardar en Base de Datos (SQL)
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO Turno (cliente_id, profesional_id, servicio_id, fecha_hora, estado) 
                VALUES (%s, %s, %s, %s, 'reservado')
            """
            cursor.execute(sql, (cliente_id, profesional_id, servicio_id, fecha_hora))
            conn.commit()
            
            nuevo_id = cursor.lastrowid
            return True, {"id": nuevo_id, "mensaje": "Turno reservado con éxito"}

        except mysql.connector.Error as err:
            return False, f"Error en la base de datos: {err}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
        finally:
            if conn:
                conn.close()
  