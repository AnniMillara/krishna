from flask import abort, flash, redirect, render_template, request, session

from db import ErrorBaseDatos
from models.peluche import Peluche


def init_peluches(app):
    @app.route("/dashboard")
    def dashboard():
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluches = Peluche.obtener_todos()
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return render_template("dashboard.html", peluches=[], total_donaciones=0), 503
        return render_template("dashboard.html", peluches=peluches,
                               total_donaciones=total_donaciones)

    @app.route("/nueva_donacion")
    def nueva_donacion():
        if "usuario_id" not in session:
            return redirect("/")
        try:
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return render_template("nueva_donacion.html", total_donaciones=0), 503
        return render_template("nueva_donacion.html", total_donaciones=total_donaciones)

    @app.route("/crear_peluche", methods=["POST"])
    def crear_peluche():
        if "usuario_id" not in session:
            return redirect("/")
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        errores = []
        if not 3 <= len(nombre) <= 100:
            errores.append("El nombre debe tener entre 3 y 100 caracteres.")
        if not 10 <= len(descripcion) <= 1000:
            errores.append("La descripción debe tener entre 10 y 1000 caracteres.")

        datos = {"nombre": nombre, "descripcion": descripcion}
        if errores:
            for error in errores:
                flash(error, "danger")
            try:
                total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total_donaciones = 0
            return render_template("nueva_donacion.html", datos=datos,
                                   total_donaciones=total_donaciones), 400

        try:
            Peluche.crear({**datos, "usuario_id": session["usuario_id"]})
        except ErrorBaseDatos:
            flash("No se pudo publicar el peluche. Intenta más tarde.", "danger")
            try:
                total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total_donaciones = 0
            return render_template("nueva_donacion.html", datos=datos,
                                   total_donaciones=total_donaciones), 503

        flash("Peluche publicado exitosamente.", "success")
        return redirect("/dashboard")

    @app.route("/editar/<int:peluche_id>")
    def editar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)
        if peluche["usuario_id"] != session["usuario_id"]:
            abort(403)
        if peluche["adoptado"]:
            flash("No puedes editar un peluche que ya fue adoptado.", "warning")
            return redirect(f"/detalle/{peluche_id}")
        return render_template("editar_donacion.html", peluche=peluche,
                               total_donaciones=total_donaciones)

    @app.route("/actualizar/<int:peluche_id>", methods=["POST"])
    def actualizar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)
        if peluche["usuario_id"] != session["usuario_id"]:
            abort(403)
        if peluche["adoptado"]:
            flash("No puedes editar un peluche que ya fue adoptado.", "warning")
            return redirect(f"/detalle/{peluche_id}")

        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        errores = []
        if not 3 <= len(nombre) <= 100:
            errores.append("El nombre debe tener entre 3 y 100 caracteres.")
        if not 10 <= len(descripcion) <= 1000:
            errores.append("La descripción debe tener entre 10 y 1000 caracteres.")
        if errores:
            for error in errores:
                flash(error, "danger")
            try:
                total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total_donaciones = 0
            peluche_editado = dict(peluche)
            peluche_editado.update(nombre=nombre, descripcion=descripcion)
            return render_template("editar_donacion.html", peluche=peluche_editado,
                                   total_donaciones=total_donaciones), 400

        try:
            resultado = Peluche.actualizar(peluche_id, {
                "nombre": nombre,
                "descripcion": descripcion,
                "usuario_id": session["usuario_id"],
            })
        except ErrorBaseDatos:
            flash("No se pudo actualizar el peluche. Intenta más tarde.", "danger")
            try:
                total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
            except ErrorBaseDatos:
                total_donaciones = 0
            peluche_editado = dict(peluche)
            peluche_editado.update(nombre=nombre, descripcion=descripcion)
            return render_template("editar_donacion.html", peluche=peluche_editado,
                                   total_donaciones=total_donaciones), 503

        if resultado == "ok":
            flash("Peluche actualizado.", "success")
        elif resultado == "sin_cambios":
            flash("No se detectaron cambios.", "info")
        elif resultado == "no_encontrado":
            abort(404)
        elif resultado == "sin_permiso":
            abort(403)
        return redirect("/dashboard")

    @app.route("/detalle/<int:peluche_id>")
    def detalle(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
            total_donaciones = Peluche.contar_donaciones(session["usuario_id"])
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)

        if peluche["usuario_id"] != session["usuario_id"]:
            try:
                Peluche.registrar_visita(peluche_id)
                peluche["visitas"] += 1
            except ErrorBaseDatos:
                # El contador no es esencial para mostrar el detalle.
                pass

        return render_template("detalle_peluche.html", peluche=peluche,
                               total_donaciones=total_donaciones)

    @app.route("/adoptar/<int:peluche_id>", methods=["POST"])
    def adoptar(peluche_id):
        if "usuario_id" not in session:
            return redirect("/")
        try:
            peluche = Peluche.obtener_por_id(peluche_id)
        except ErrorBaseDatos:
            flash("Servicio temporalmente no disponible. Intenta más tarde.", "danger")
            return redirect("/dashboard")
        if not peluche:
            abort(404)
        if peluche["usuario_id"] == session["usuario_id"]:
            abort(403)

        try:
            adoptado = Peluche.adoptar(peluche_id, session["usuario_id"])
        except ErrorBaseDatos:
            flash("No se pudo completar la adopción. Intenta más tarde.", "danger")
            return redirect("/dashboard")

        if adoptado:
            flash("¡Has adoptado este peluche!", "success")
        else:
            flash("Este peluche ya fue adoptado o no está disponible.", "warning")
        return redirect("/dashboard")
