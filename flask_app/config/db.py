import os
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

class MySQLConnection:
    def __init__(self, db):
        self.db = db

    def query_db(self, query, data=None):
        try:
            connection = pymysql.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=self.db,
                port=int(os.getenv("DB_PORT")),
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        except Exception as e:
            print(f"Error de conexión a MySQL: {e}")
            raise Exception("No se pudo conectar a la base de datos.")

        with connection.cursor() as cursor:
            try:
                q = query.strip().lower()
                cursor.execute(query, data)
                if q.startswith("select"):
                    return cursor.fetchall()
                if q.startswith("insert"):
                    return cursor.lastrowid
                return cursor.rowcount
            except Exception as e:
                print("Error en la consulta SQL:", e)
                raise Exception("Error interno al procesar la solicitud en la base de datos.")
            finally:
                connection.close()

def connectToMySQL(db):
    return MySQLConnection(db)