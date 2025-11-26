from api.db.db_config import get_db_connection
import mysql.connector
class Usuario:
    schema = {
        "name": str,
        "email": str,
        "password": str,
        "negocio_id": int,
        "id": int}
         
    def __init__(self, id, nombre, email):
        self.id = id
        self.nombre = nombre
        self.email = email
        pass
    @classmethod
    def obtener_por_id(cursor, id):
        sql = "SELECT id, nombre, email FROM Usuario WHERE id = %s"
        cursor.execute(sql, (id,))
        user_data = cursor.fetchone() # Asegúrate que el cursor sea dictionary=True
        
        if user_data:
            # Retornamos el diccionario directo o un objeto, como prefieras.
            # Para simplificar, devolvemos el diccionario:
            return user_data
        return None

    @classmethod
    def get_todos_los_usuarios(cls):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email FROM usuario")
        filas = cursor.fetchall()
        cursor.close()
        connection.close()
        usuarios = [Usuario(fila).to_json() for fila in filas]
        return usuarios
    @classmethod
    def get_todos_los_usuarios(cls):
        """Obtiene todos los usuarios de la base de datos."""
        query = "SELECT id, name AS nombre, email, negocio_id FROM Usuario"
        
        conn = None
        try:
            conn = get_db_connection()
            if conn is None:
                return []
                
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            resultados = cursor.fetchall() 
            return resultados
            
        except mysql.connector.Error as err:
            print(f"Error en get_todos_los_usuarios: {err}")
            return []
        finally:
            if conn:
                if 'cursor' in locals() and cursor:
                    cursor.close()
                conn.close()


    @classmethod 
    def validar(cls, datos):
        if datos is None or type (datos) != dict:
            return False, "Datos inválidos"
        for key in cls.schema:
            if key not in datos:
                return False, f"Falta el campo: {key}"
            if type(datos[key]) != cls.schema[key]:
                return False, f"Tipo inválido para el campo: {key}"
        

    def __init__(self, fila):
        self.__id = fila['0']
        self.__nombre = fila['1']
        self.__email = fila['2']
        self.__password = fila['3'] 

    @classmethod 
    def post_usuario(cls, datos):
        if not cls.validar(datos):
            return jsonify({"error": "Datos inválidos"}), 400
        
        pass


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
        

        #control dni

        dni = datos['dni']
        cursor.execute("SELECT id FROM usuario WHERE dni = %s AND id != %s", (dni,))
        fila= cursor.fetchone()
        if fila:
            raise ValueError("El DNI ya está en uso por otro usuario")
        

    def registrar(self, cursor):
        sql = "INSERT INTO usuario (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (self.nombre, self.email, self.password))
        self.id = cursor.lastrowid
        return self.id

    @staticmethod
    def login(cursor, email, password_ingresada):
        sql = "SELECT * FROM usuario WHERE email = %s"
        cursor.execute(sql, (email,))
        user_data = cursor.fetchone()

        if user_data and user_data['password'] == password_ingresada:
            return Usuario(
                id=user_data['id'],
                nombre=user_data['nombre'],
                email=user_data['email'],
                password=user_data['contrasena']
            )
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email
            # No devolvemos la contraseña aquí por un mínimo de decencia visual
        }