from flask import Flask
from flask import jsonify
from flask_cors import CORS
 
app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"]
    }
})
@app.route('/')

def  test():
    return jsonify({"mensaje": "ruta del index"})

app.config['SECRET_KEY'] = "clave_api"
import api.routes.Cliente
import api.routes.Disponibilidad
import api.routes.Usuario
import api.routes.Negocio
import api.routes.profesional
import api.routes.Servicio
import api.routes.Turno
