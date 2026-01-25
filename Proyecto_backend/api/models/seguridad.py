from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 1. Ignorar OPTIONS (CORS)
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        # 2. DEBUG: Ver qué llega en los headers
        auth_header = request.headers.get('Authorization')
        print(f"\n--- DEBUG SEGURIDAD ({request.path}) ---")
        print(f"Header Authorization recibido: {auth_header}")

        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                print("DEBUG ERROR: El header no tiene el formato 'Bearer <token>'")
                return jsonify({'message': 'Formato de token inválido'}), 401
        
        if not token:
            print("DEBUG ERROR: No se encontró token en la petición")
            return jsonify({'message': 'Token faltante'}), 401

        try:
            # 3. Intentar decodificar con la clave centralizada
            clave = current_app.config['SECRET_KEY']
            print(f"DEBUG: Usando clave secreta: {clave}")
            
            data = jwt.decode(token, clave, algorithms=["HS256"])
            
            print(f"DEBUG EXITO: Token válido para usuario ID {data['id']}")
            
            current_user = {
                'id': data['id'],
                'negocio_id': data['negocio_id'],
                'rol': data['rol']
            }
        except jwt.ExpiredSignatureError:
            print("DEBUG ERROR: El token expiró")
            return jsonify({'message': 'Token expirado', 'error': 'expired'}), 401
        except jwt.InvalidTokenError as e:
            print(f"DEBUG ERROR: Token inválido. Razón: {e}")
            return jsonify({'message': 'Token inválido'}), 401
        except Exception as e:
            print(f"DEBUG ERROR CRITICO: {e}")
            return jsonify({'message': 'Error de token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated