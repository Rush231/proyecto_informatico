from api.db.db_config import get_db_connection
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from api import app
import jwt
from datetime import datetime, timedelta, timezone 
import traceback # Para ver errores detallados si ocurren

class Usuario:
    @classmethod
    def login(cls, auth):
        conn = None
        try:
            # 1. Validar si 'auth' es dict o objeto
            username = auth.get('username') if isinstance(auth, dict) else auth.username
            password = auth.get('password') if isinstance(auth, dict) else auth.password

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 2. Buscar usuario
            sql = "SELECT id, name, password, rol, negocio_id FROM Usuario WHERE name = %s"
            cursor.execute(sql, (username,))
            user_data = cursor.fetchone()

            if not user_data:
                raise ValueError("Usuario no encontrado")

            if not check_password_hash(user_data['password'], password):
                raise ValueError("Contraseña incorrecta")
            
            # --- DEBUG: Verificamos qué trae la base de datos ---
            print("--- DEBUG LOGIN: DATOS DB ---")
            print(user_data) 
            
            # 3. Definir la variable token_payload (CORREGIDO EL USO DE DATETIME)
            # Asegúrate de usar 'datetime.now(timezone.utc)' si importaste 'from datetime import datetime'
            # O 'datetime.datetime.now(...)' si importaste 'import datetime'
            # Aquí uso la forma compatible con tu archivo:
            token_payload = {
                'id': user_data['id'],
                'name': user_data['name'], 
                'rol': user_data.get('rol', 'empleado'), 
                'negocio_id': user_data['negocio_id'],
                'exp': datetime.now(timezone.utc) + timedelta(hours=8)
            }

            # --- DEBUG: Verificamos el payload YA CREADO ---
            print("--- DEBUG LOGIN: PAYLOAD ---")
            print(token_payload) 
            
            # 4. Generar Token
            TOKEN = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
            
            return {
                'token': TOKEN,
                'id': user_data['id'],
                'name': user_data['name'],
                'rol': user_data.get('rol', 'empleado'),
                'negocio_id': user_data['negocio_id']
            }

        except Exception as e:
            # Importante: Imprimimos el error real
            import traceback
            traceback.print_exc()
            print(f"Error en login: {e}") 
            return None 
        finally:
            if conn: conn.close()

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
        
