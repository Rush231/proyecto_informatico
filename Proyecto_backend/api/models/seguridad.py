from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        #  Buscar el token en el Header 'Authorization'
        if 'Authorization' in request.headers:
            # El formato estándar es "Bearer <token>"
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1] 
        
        if not token:
            return jsonify({'message': 'Token faltante, inicie sesión'}), 401
        
        try:
            #  Decodificar usando la clave secreta de la app
            # Usamos current_app para acceder a la config sin importar 'app' directamente
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # 3. Guardar datos críticos en 'g' (variable global de la request)
            g.usuario_id = data.get('id')
            g.negocio_id = data.get('negocio_id') #  Tu filtro de seguridad
            g.rol = data.get('rol')
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Su sesión ha expirado'}), 401
        except Exception as e:
            return jsonify({'message': 'Token inválido'}), 401
            
        return f(*args, **kwargs)
    return decorated