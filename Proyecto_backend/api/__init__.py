from flask import Flask
from flask import jsonify

 
app = Flask(__name__)

@app.route('/')
def  test():
    return jsonify({"mensaje": "ruta del index"})

import api.routes.Cliente
import api.routes.Disponibilidad
import api.routes.Usuario
import api.routes.Negocio
import api.routes.profesional
import api.routes.Servicio
import api.routes.Turno
