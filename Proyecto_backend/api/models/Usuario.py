from api.db.db_config import get_db_connection
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from api import app
from datetime import datetime, timezone, timedelta
import jwt


app.config['SECRET_KEY'] = "clave_api"


class Usuario:
    # Esquema para validación
    schema = {
        "name": str,
        "email": str,
        "password": str,}

    # Un único constructor que maneja los datos
    def __init__(self, id, name, email, password=None, negocio_id=None, rol='empleado'):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.negocio_id = negocio_id
        self.rol = rol

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
    def get_todos_los_usuarios(cls, negocio_id):
        query = "SELECT id, name AS nombre, email, negocio_id FROM Usuario WHERE negocio_id = %s"
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
            
            # 1. Buscamos usuario y traemos negocio_id y rol
            sql = "SELECT id, name, password, rol, negocio_id FROM Usuario WHERE name = %s"
            cursor.execute(sql, (auth.username,))
            user_data = cursor.fetchone()

            if not user_data:
                raise ValueError("Usuario no encontrado")

            if not check_password_hash(user_data['password'], auth.password):
                raise ValueError("Contraseña incorrecta")
            
            # 2. INYECTAMOS EL NEGOCIO_ID EN EL TOKEN (Crucial para SaaS)
            token_payload = {
                'id': user_data['id'],
                'name': user_data['name'], 
                'rol': user_data['rol'],
                'negocio_id': user_data['negocio_id'], # <--- AQUÍ ESTÁ LA MAGIA DEL SAAS
                'exp': datetime.now(timezone.utc) + timedelta(hours=8)
            }
            
            TOKEN = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
            
            return {
                'token': TOKEN,
                'id': user_data['id'],
                'name': user_data['name'],
                'rol': user_data['rol'],
                'negocio_id': user_data['negocio_id']
            }

        except Exception as e:
            print(f"Error en login: {e}") 
            return None 
        finally:
            if conn: conn.close()

    @classmethod
    def get_usuarios_por_negocio(cls, negocio_id):
        # CAMBIO: Antes traía todos (peligroso en SaaS). Ahora filtra por negocio.
        query = "SELECT id, name AS nombre, email, rol FROM Usuario WHERE negocio_id = %s"
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (negocio_id,))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
        finally:
            if conn: conn.close()

    @classmethod
    def registrar_usuario_saas(cls, datos):
        # Este método asume que el Negocio YA existe o se crea en una transacción superior.
        # Aquí solo insertamos el usuario vinculado.
        username = datos['name']
        password = datos['password']
        email = datos['email']
        negocio_id = datos.get('negocio_id')
        rol = datos.get('rol', 'admin') # Primer usuario suele ser admin

        if not negocio_id:
            raise ValueError("Falta el ID del negocio")

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Verificación básica de unicidad (puedes mejorarla)
            cursor.execute("SELECT id FROM Usuario WHERE email = %s", (email,))
            if cursor.fetchone():
                raise ValueError("El email ya existe")

            sql = "INSERT INTO Usuario (name, email, password, negocio_id, rol) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (username, email, hashed_password, negocio_id, rol))
            conn.commit()
            return cursor.lastrowid
        finally:
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
        
