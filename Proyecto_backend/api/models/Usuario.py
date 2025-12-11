from api.db.db_config import get_db_connection
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from api import app
import jwt
import datetime


app.config['SECRET_KEY'] = "clave_api"


class Usuario:
    # Esquema para validación
    schema = {
        "name": str,
        "email": str,
        "password": str,}

    # Un único constructor que maneja los datos
    def __init__(self, id, name, email, password=None, negocio_id=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.negocio_id = negocio_id

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.name,
            "email": self.email,
        }
    @classmethod
    def validar(cls, datos):
        if datos is None or not isinstance(datos, dict):
            return False, "Datos inválidos o vacíos"
        
        for key, expected_type in cls.schema.items():
            if key not in datos:
                return False, f"Falta el campo obligatorio: {key}"
            if not isinstance(datos[key], expected_type):
                return False, f"Tipo inválido para el campo: {key}"
            if expected_type == str and not datos[key].strip():
                return False, f"El campo {key} no puede estar vacío"
            if key == 'password' and len(datos[key]) < 8:
                return False, "La contraseña debe tener al menos 8 caracteres"
        return True, "Datos válidos"

    @classmethod
    def usuario_por_id(cls, id):
        sql = "SELECT id, name, email, password, negocio_id FROM Usuario WHERE id = %s"
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (id,))
            user_data = cursor.fetchone()
        
            if user_data:
                return user_data
            return None 
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_todos_los_usuarios(cls):
        query = "SELECT id, name AS nombre, email, negocio_id FROM Usuario"
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados
        except mysql.connector.Error as err:
            print(f"Error en get_todos_los_usuarios: {err}")
            return []
        finally:
            if conn:
                conn.close()




    @classmethod 
    def post_usuario(cls, datos):
        # 1. Validar datos
        valido, mensaje = cls.validar(datos)
        if not valido:
            return None, mensaje # Devolvemos error al controlador
        
        # 2. Insertar en BD
        sql = "INSERT INTO Usuario (name, email, password, negocio_id) VALUES (%s, %s, %s, %s)"
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, (datos['nombre'], datos['email'], datos['password'], datos.get('negocio_id')))
            conn.commit()
            
            # Retornamos el ID del nuevo usuario
            return cursor.lastrowid, "Usuario creado exitosamente"
        except mysql.connector.Error as err:
            return None, f"Error de BD: {err}"
        finally:
            if conn:
                conn.close()

    @classmethod
    def put_usuario(cls, id, datos):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor
        if not cls.validar(datos):
           raise ValueError("Datos inválidos")
        

        #control de id

        cursor.execute("SELECT id FROM usuario WHERE id = %s", (id,))

        #control email


        email = datos['email']
        cursor.execute("SELECT id FROM usuario WHERE email = %s AND id != %s", (email,)) 
        fila= cursor.fetchone()
        if fila:
            raise ValueError("El email ya está en uso por otro usuario")
        
    @classmethod
    def registrar(cls, datos):
        if not cls.validar(datos):
            raise ValueError("Datos inválidos")
        username = datos['name']
        password = datos['password']
        email = datos['email']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM usuario WHERE name = %s", (username,))
        fila = cursor.fetchone()
        if fila is not None:
            raise ValueError("El nombre de usuario ya existe")
        
        hashed_password = generate_password_hash(password, method= 'pbkdf2:sha256')
        negocio_id = datos.get('negocio_id')
        
        cursor.execute("INSERT INTO usuario (name, password, email) VALUES (%s, %s, %s)", (username,hashed_password ,email))
        connection.commit()

        cursor.close()
        connection.close()
    


    @classmethod
    def login(cls, auth):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Buscamos por nombre de usuario E INCLUIMOS EL ROL
            sql = "SELECT id, name, password, rol FROM usuario WHERE name = %s" # <--- CAMBIO AQUÍ
            cursor.execute(sql, (auth.username,))
            user_data = cursor.fetchone()

            if not user_data:
                raise ValueError("Usuario no encontrado")

            password_bd = user_data['password']
            
            if not check_password_hash(password_bd, auth.password):
                raise ValueError("Contraseña incorrecta")
            
            # . Token Payload
            token_payload = {
                'name': user_data['name'], 
                'id': user_data['id'],
                'rol': user_data['rol'], # <--- Útil para validaciones en backend
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
            }
            
            TOKEN = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
            
            # Retornamos el rol para que el JS lo pueda leer
            return {
                'token': TOKEN,
                'id': user_data['id'],
                'name': user_data['name'],
                'rol': user_data['rol']  # <--- IMPORTANTE: Enviar el rol al frontend
            }

        except Exception as e:
            print(f"Error en login: {e}") 
            return None 
        finally:
            if conn:
                conn.close()

    @classmethod
    def eliminar(cls, id):
        sql = "DELETE FROM Usuario WHERE id = %s"
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, (id,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error eliminar_usuario: {err}")
            return False
        finally:
            if conn:
                conn.close()
        
