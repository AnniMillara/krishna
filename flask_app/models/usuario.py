import re
from flask_app.config.db import connectToMySQL

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NOMBRE_REGEX = re.compile(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*\d).{8,}$')

DB = "familia_peluche"

class Usuarios:
    def __init__(self, data):
        self.id_usuario = data["id_usuario"]
        self.nombre = data["nombre"]
        self.apellido = data["apellido"]
        self.email = data["email"]
        self.contrasena = data["contrasena"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

    @classmethod
    def guardar(cls, data):
        query = """
            INSERT INTO usuarios (nombre, apellido, email, contrasena, created_at, updated_at) 
            VALUES (%(nombre)s, %(apellido)s, %(email)s, %(contrasena)s, NOW(), NOW());
        """
        return connectToMySQL(DB).query_db(query, data)

    @classmethod
    def buscar_email(cls, email):
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        data = {"email": email}
        resultado = connectToMySQL(DB).query_db(query, data)
        if resultado:
            return cls(resultado[0])
        return None

    @staticmethod
    def validar_registro(datos):
        errores = []

        if not datos["nombre"]:
            errores.append("El nombre es obligatorio.")
        elif not NOMBRE_REGEX.match(datos["nombre"]):
            errores.append("El nombre solo debe contener letras.")
        elif len(datos["nombre"]) < 2 or len(datos["nombre"]) > 60:
            errores.append("El nombre debe tener entre 2 y 60 caracteres.")

        if not datos["apellido"]:
            errores.append("El apellido es obligatorio.")
        elif not NOMBRE_REGEX.match(datos["apellido"]):
            errores.append("El apellido solo debe contener letras.")
        elif len(datos["apellido"]) < 2 or len(datos["apellido"]) > 60:
            errores.append("El apellido debe tener entre 2 y 60 caracteres.")

        if not datos["email"]:
            errores.append("El email es obligatorio.")
        elif not EMAIL_REGEX.match(datos["email"]):
            errores.append("El email no tiene un formato válido.")
        elif len(datos["email"]) > 200:
            errores.append("El email no puede superar los 200 caracteres.")
        elif Usuarios.buscar_email(datos["email"]):
            errores.append("El correo ya está registrado.")

        if not datos["contrasena"]:
            errores.append("La contraseña es obligatoria.")
        elif not PASSWORD_REGEX.match(datos["contrasena"]):
            errores.append("La contraseña debe tener al menos 8 caracteres, una mayúscula y un número.")
        elif datos["contrasena"] != datos.get("confirmar_contrasena", ""):
            errores.append("Las contraseñas no coinciden.")

        return errores