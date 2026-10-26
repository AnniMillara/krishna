import os

from flask import Flask, render_template
from dotenv import load_dotenv

from controllers.peluches import init_peluches
from controllers.usuarios import init_usuarios
from extensions import bcrypt, csrf

load_dotenv()

app = Flask(__name__, template_folder="templates")
secret_key = os.getenv("SECRET_KEY")
if not secret_key or len(secret_key) < 32:
    raise RuntimeError("Configura SECRET_KEY en .env con al menos 32 caracteres aleatorios.")
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "false").lower() == "true"

bcrypt.init_app(app)
csrf.init_app(app)
init_usuarios(app)
init_peluches(app)


@app.errorhandler(403)
def prohibido(error):
    return render_template("error.html", codigo=403,
                           mensaje="No tienes permiso para acceder aquí."), 403


@app.errorhandler(404)
def no_encontrado(error):
    return render_template("error.html", codigo=404,
                           mensaje="La página que buscas no existe."), 404


@app.errorhandler(500)
def error_interno(error):
    return render_template("error.html", codigo=500,
                           mensaje="Ocurrió un error inesperado. Intenta más tarde."), 500


if __name__ == "__main__":
    app.run(debug=False)
