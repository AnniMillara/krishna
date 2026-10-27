from flask import render_template, redirect, request, session, flash, url_for
from flask_app import app, bcrypt
from flask_app.models.usuario import Usuarios

@app.route("/")
def inicio():
    if "id_usuario" in session:
        return redirect(url_for("peluches"))
    return render_template("login.html")

@app.route("/registro", methods=["POST"])
def registro():
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "apellido": request.form.get("apellido", "").strip(),
        "email": request.form.get("email", "").strip(),
        "contrasena": request.form.get("contrasena", "").strip(),
        "confirmar_contrasena": request.form.get("confirmar_contrasena", "").strip(),
    }
    
    errores = Usuarios.validar_registro(datos)
    if errores:
        for error in errores:
            flash(error, "danger")
        return render_template("login.html", form_data=datos)

    hash_pw = bcrypt.generate_password_hash(datos["contrasena"]).decode("utf-8")
    data = {
        "nombre": datos["nombre"],
        "apellido": datos["apellido"],
        "email": datos["email"],
        "contrasena": hash_pw,
    }
    
    try:
        nuevo_id = Usuarios.guardar(data)
        if not nuevo_id:
            raise ValueError("No se pudo obtener el ID.")
        session["id_usuario"] = nuevo_id
        session["nombre"] = datos["nombre"]
        flash("¡Bienvenid@ a Donación★Peluches!", "success")
        return redirect(url_for("peluches"))
    except Exception:
        flash("Error interno al crear la cuenta.", "danger")
        return render_template("login.html", form_data=datos)

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip()
    contrasena = request.form.get("contrasena", "").strip()

    if not email or not contrasena:
        flash("Email y contraseña son obligatorios.", "danger")
        return redirect(url_for("inicio"))

    try:
        usuario = Usuarios.buscar_email(email)
        if not usuario or not bcrypt.check_password_hash(usuario.contrasena, contrasena):
            flash("Email o contraseña incorrectos.", "danger")
            return redirect(url_for("inicio"))

        session["id_usuario"] = usuario.id_usuario
        session["nombre"] = usuario.nombre
        flash("Bienvenido de vuelta.", "success")
        return redirect(url_for("peluches"))
    except Exception:
        flash("Error de conexión.", "danger")
        return redirect(url_for("inicio"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("inicio"))