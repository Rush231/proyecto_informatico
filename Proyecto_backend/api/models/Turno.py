from datetime import datetime, timedelta, date
from api.db.db_config import get_db_connection
import mysql.connector
from datetime import datetime, timedelta
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        #Identificar qué día de la semana es (0=Lunes, 6=Domingo)
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        dia_semana = fecha_obj.weekday()

        try:
            # Obtener la regla general de disponibilidad para ese día
            sql_dispo = "SELECT hora_inicio, hora_fin FROM Disponibilidad WHERE profesional_id = %s AND dia_semana = %s"
            cursor.execute(sql_dispo, (profesional_id, dia_semana))
            reglas = cursor.fetchall()

            if not reglas:
                return [] # El profesional no trabaja ese día
            

            sql_turnos = """
                SELECT t.fecha_hora, s.duracion 
                FROM Turno t
                JOIN Servicio s ON t.servicio_id = s.id
                WHERE t.profesional_id = %s 
                AND DATE(t.fecha_hora) = %s 
                AND t.estado != 'cancelado'
            """
            cursor.execute(sql_turnos, (profesional_id, fecha_str))
            ocupados = cursor.fetchall()

            # Bloqueos (Feriados/Ausencias)
            sql_bloqueos = """
                SELECT fecha_inicio, fecha_fin FROM BloqueoAgenda 
                WHERE profesional_id = %s 
                AND (DATE(fecha_inicio) <= %s AND DATE(fecha_fin) >= %s)
            """
            cursor.execute(sql_bloqueos, (profesional_id, fecha_str, fecha_str))
            bloqueos = cursor.fetchall()

            horarios_disponibles = []

            # Iteramos por CADA rango de disponibilidad (ej: primero mañana, luego tarde)
            for regla in reglas:
                def asegurar_time(valor):
                    if isinstance(valor, timedelta):
                        return (datetime.min + valor).time()
                    if isinstance(valor, str):
                        # Parche para cuando la DB devuelve strings tipo "09:00:00"
                        try:
                            return datetime.strptime(valor, "%H:%M:%S").time()
                        except ValueError:
                             # Intento alternativo para formato corto "09:00"
                            return datetime.strptime(valor, "%H:%M").time()
                    return valor
                
                hora_inicio_time = asegurar_time(regla['hora_inicio'])
                hora_fin_time = asegurar_time(regla['hora_fin'])

             # Combinamos con la fecha para tener datetime completos
                inicio_jornada = datetime.combine(fecha_obj, hora_inicio_time)
                fin_jornada = datetime.combine(fecha_obj, hora_fin_time)
                tiempo_actual = inicio_jornada
                # Barrido de slots
                while tiempo_actual + timedelta(minutes=duracion_minutos) <= fin_jornada:
                    tiempo_fin_turno = tiempo_actual + timedelta(minutes=duracion_minutos)
                    esta_libre = True

                    # A. Verificar colisión REAL con Turnos existentes (Superposición de rangos)
                    for turno in ocupados:
                        inicio_ocupado = turno['fecha_hora']
                        fin_ocupado = inicio_ocupado + timedelta(minutes=turno['duracion'])
                        
                        # Lógica de superposición: (InicioA < FinB) y (FinA > InicioB)
                        if (tiempo_actual < fin_ocupado) and (tiempo_fin_turno > inicio_ocupado):
                            esta_libre = False
                            break

                    # B. Verificar colisión con Bloqueos
                    if esta_libre:
                        for bloque in bloqueos:
                            b_inicio = bloque['fecha_inicio']
                            b_fin = bloque['fecha_fin']
                            if (tiempo_actual < b_fin) and (tiempo_fin_turno > b_inicio):
                                esta_libre = False
                                break
                    
                    if esta_libre:
                        horarios_disponibles.append(tiempo_actual.strftime('%H:%M'))
                    
                    tiempo_actual += timedelta(minutes=duracion_minutos) # O usa intervalo fijo (ej: 15 o 30 min)

            # Ordenar y eliminar duplicados si los hubiera
            return sorted(list(set(horarios_disponibles)))
        

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
                return False, "El horario seleccionado no esta disponible (ocupado, feriado o fuera de rango)."

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

    @classmethod
    def obtener_por_cliente(cls, cliente_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Traemos los datos cruzando tablas para obtener los nombres
            query = """
                SELECT 
                    t.id, 
                    t.fecha_hora, 
                    s.name AS servicio, 
                    p.name AS profesional, 
                    n.name AS negocio
                FROM Turno t
                JOIN Servicio s ON t.servicio_id = s.id
                JOIN Profesional p ON t.profesional_id = p.id
                JOIN Negocio n ON s.negocio_id = n.id
                WHERE t.cliente_id = %s
                ORDER BY t.fecha_hora DESC
            """
            
            cursor.execute(query, (cliente_id,))
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            
            # Formateamos la fecha para que se vea bien en JSON
            for turno in result:
                if turno['fecha_hora']:
                    turno['fecha_hora'] = turno['fecha_hora'].strftime('%Y-%m-%d %H:%M')
            
            return result

        except Exception as e:
            print(f"Error al obtener turnos: {e}")
            return []
  

    @classmethod
    def obtener_slots_calendario(cls, profesional_id, servicio_id, fecha_inicio_str, fecha_fin_str):
        """
        Genera la estructura de eventos compatible con FullCalendar para un rango de fechas.
        Retorna: Lista de diccionarios.
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Obtener duración del servicio
            cursor.execute("SELECT duracion FROM Servicio WHERE id = %s", (servicio_id,))
            servicio = cursor.fetchone()
            duracion = servicio['duracion'] if servicio else 30
            
            eventos = []
            
            # Convertir strings a objetos fecha
            # FullCalendar suele enviar fechas con hora (ej: 2023-11-20T00:00:00), cortamos la parte de la fecha
            fecha_actual = datetime.strptime(fecha_inicio_str.split('T')[0], '%Y-%m-%d')
            fecha_limite = datetime.strptime(fecha_fin_str.split('T')[0], '%Y-%m-%d')

            # 2. Iterar por cada día del rango
            while fecha_actual <= fecha_limite:
                fecha_str = fecha_actual.strftime('%Y-%m-%d')
                
                # Reutilizamos tu lógica existente que ya busca huecos libres y valida bloqueos
                horarios = cls.buscar_horarios_disponibles(profesional_id, fecha_str, duracion)
                
                for hora in horarios:
                    inicio_iso = f"{fecha_str}T{hora}"
                    hora_dt = datetime.strptime(inicio_iso, '%Y-%m-%dT%H:%M')
                    fin_dt = hora_dt + timedelta(minutes=duracion)
                    
                    eventos.append({
                        "title": "Disponible",
                        "start": inicio_iso,
                        "end": fin_dt.strftime('%Y-%m-%dT%H:%M'),
                        "color": "#28a745", # Verde
                        "textColor": "white",
                        # "extendedProps": { "servicio_id": servicio_id } # Útil si necesitas más datos en el click
                    })
                
                fecha_actual += timedelta(days=1)
                
            return eventos

        except Exception as e:
            print(f"Error en obtener_slots_calendario: {e}")
            return [] # Retornar lista vacía en caso de error para no romper el front
        finally:
            if conn:
                conn.close()