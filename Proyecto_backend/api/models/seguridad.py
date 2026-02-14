from functools import wraps
from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # ¡ELIMINAMOS EL BLOQUE DE OPTIONS DE AQUÍ!
        
        auth_header = request.headers.get('Authorization')
        
        print(f"--- DEBUG SEGURIDAD ({request.path}) ---")
        print(f"Método HTTP: {request.method}")
        print(f"Header Authorization recibido: {auth_header}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            print("DEBUG ERROR: No se encontró token o el formato no es 'Bearer <token>'")
            return jsonify({'message': 'Token faltante, inicie sesión'}), 401
        
        token = auth_header.split(" ")[1] 
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            g.usuario_id = data.get('id')
            g.negocio_id = data.get('negocio_id') 
            g.rol = data.get('rol')
            
        except jwt.ExpiredSignatureError:
            print("DEBUG ERROR: El token expiró")
            return jsonify({'message': 'Su sesión ha expirado'}), 401
        except Exception as e:
            print(f"DEBUG ERROR: {e}")
            return jsonify({'message': 'Token inválido'}), 401
            
        return f(*args, **kwargs)
    return decorated