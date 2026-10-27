from flask_app.config.db import connectToMySQL

DB = "familia_peluche"

class Peluches:
    def __init__(self, data):
        self.id_peluche = data["id_peluche"]
        self.nombre = data["nombre"]
        self.descripcion = data["descripcion"]
        self.visitas = data.get("visitas", 0)
        self.donador_id = data.get("donador_id")
        self.adoptador_id = data.get("adoptador_id")
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.donador_nombre = data.get("donador_nombre")
        self.donador_apellido = data.get("donador_apellido")
        self.adoptador_nombre = data.get("adoptador_nombre")
        self.adoptador_apellido = data.get("adoptador_apellido")

    @classmethod
    def guardar(cls, data):
        query = """
            INSERT INTO peluches (nombre, descripcion, donador_id, created_at, updated_at) 
            VALUES (%(nombre)s, %(descripcion)s, %(donador_id)s, NOW(), NOW());
        """
        return connectToMySQL(DB).query_db(query, data)

    @classmethod
    def ver_todas(cls):
        query = """
            SELECT p.*, d.nombre AS donador_nombre, d.apellido AS donador_apellido,
                   a.nombre AS adoptador_nombre, a.apellido AS adoptador_apellido
            FROM peluches p
            LEFT JOIN usuarios d ON p.donador_id = d.id_usuario
            LEFT JOIN usuarios a ON p.adoptador_id = a.id_usuario
            ORDER BY p.id_peluche;
        """
        resultados = connectToMySQL(DB).query_db(query)
        return [cls(fila) for fila in resultados] if resultados else []

    @classmethod
    def buscar_id(cls, id):
        query = """
            SELECT p.*, d.nombre AS donador_nombre, d.apellido AS donador_apellido,
                   a.nombre AS adoptador_nombre, a.apellido AS adoptador_apellido
            FROM peluches p
            LEFT JOIN usuarios d ON p.donador_id = d.id_usuario
            LEFT JOIN usuarios a ON p.adoptador_id = a.id_usuario
            WHERE p.id_peluche = %(id_peluche)s;
        """
        resultado = connectToMySQL(DB).query_db(query, {"id_peluche": id})
        return cls(resultado[0]) if resultado else None

    @classmethod
    def buscar_por_nombre_y_donador(cls, nombre, donador_id, excluir_id=None):
        if excluir_id:
            query = "SELECT * FROM peluches WHERE nombre=%(nombre)s AND donador_id=%(donador_id)s AND id_peluche!=%(id_peluche)s;"
            data = {"nombre": nombre, "donador_id": donador_id, "id_peluche": excluir_id}
        else:
            query = "SELECT * FROM peluches WHERE nombre=%(nombre)s AND donador_id=%(donador_id)s;"
            data = {"nombre": nombre, "donador_id": donador_id}
        resultado = connectToMySQL(DB).query_db(query, data)
        return cls(resultado[0]) if resultado else None

    @classmethod
    def modificar(cls, data):
        query = "UPDATE peluches SET nombre=%(nombre)s, descripcion=%(descripcion)s, updated_at=NOW() WHERE id_peluche=%(id_peluche)s AND donador_id=%(donador_id)s;"
        return connectToMySQL(DB).query_db(query, data)

    @classmethod
    def adoptar(cls, data):
        query = "UPDATE peluches SET adoptador_id=%(adoptador_id)s, updated_at=NOW() WHERE id_peluche=%(id_peluche)s;"
        return connectToMySQL(DB).query_db(query, data)

    @classmethod
    def sumar_visita(cls, id):
        query = "UPDATE peluches SET visitas = visitas + 1 WHERE id_peluche = %(id_peluche)s;"
        return connectToMySQL(DB).query_db(query, {"id_peluche": id})

    @classmethod
    def eliminar(cls, id, donador_id):
        query = "DELETE FROM peluches WHERE id_peluche=%(id_peluche)s AND donador_id=%(donador_id)s;"
        return connectToMySQL(DB).query_db(query, {"id_peluche": id, "donador_id": donador_id})

    @staticmethod
    def validar(datos):
        errores = []
        if not datos["nombre"]:
            errores.append("El nombre es obligatorio.")
        elif len(datos["nombre"]) < 2 or len(datos["nombre"]) > 60:
            errores.append("El nombre debe tener entre 2 y 60 caracteres.")

        if not datos["descripcion"]:
            errores.append("La descripción es obligatoria.")
        elif len(datos["descripcion"]) < 10 or len(datos["descripcion"]) > 250:
            errores.append("La descripción debe tener entre 10 y 250 caracteres.")

        if datos.get("donador_id") and datos["nombre"]:
            existente = Peluches.buscar_por_nombre_y_donador(datos["nombre"], datos["donador_id"], datos.get("id_peluche"))
            if existente:
                errores.append("Ya tienes un peluche registrado con ese nombre.")
        return errores