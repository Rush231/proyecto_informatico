from api.db.db_config import get_db_connection
class Usuario:
    schema = {
        "name": str,
        "email": str,
        "password": str,
        "negocio_id": int}
    def __init__(self, id, nombre, email):
        self.id = id
        self.nombre = nombre
        self.email = email
        pass
    @classmethod
    def get_usuario_por_id(cls, id):
        return {"name": "padre", "dni": 123}
    

    @classmethod
    def get_todos_los_usuarios(cls):
        return [
            {"name": "padre", "dni": 123},
            {"name": "madre", "dni": 456},
            {"name": "hijo", "dni": 789}
        ]
    

    @classmethod 
    def post_usuario():
        pass


    @classmethod
    def put_usuario():
        pass
