from flask import render_template, redirect, request, session, flash, url_for
from flask_app import app
from flask_app.models.peluche import Peluches

@app.route("/peluche")
def peluches():
    if "id_usuario" not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("inicio"))
    try:
        return render_template("peluche_lista.html", peluches=Peluches.ver_todas())
    except Exception:
        flash("Error al cargar el listado.", "danger")
        return redirect(url_for("inicio"))

@app.route("/peluche/nuevo")
def nuevo_peluche():
    if "id_usuario" not in session:
        return redirect(url_for("inicio"))
    return render_template("peluche_form.html", peluche=None)

@app.route("/peluche/crear", methods=["POST"])
def crear_peluche():
    if "id_usuario" not in session:
        return redirect(url_for("inicio"))

    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "donador_id": session["id_usuario"]
    }
    
    errores = Peluches.validar(datos)
    if errores:
        for error in errores:
            flash(error, "danger")
        return render_template("peluche_form.html", peluche=datos)

    try:
        Peluches.guardar(datos)
        flash("¡Gracias por donar un peluche!", "success")
        return redirect(url_for("peluches"))
    except Exception:
        flash("Error al guardar.", "danger")
        return render_template("peluche_form.html", peluche=datos)

@app.route("/peluche/detalle/<int:id>")
def detalle_peluche(id):
    if "id_usuario" not in session:
        return redirect(url_for("inicio"))

    try:
        peluche = Peluches.buscar_id(id)
        if not peluche:
            flash("Peluche no encontrado.", "danger")
            return redirect(url_for("peluches"))

        if peluche.donador_id != session["id_usuario"]:
            Peluches.sumar_visita(id)
            peluche = Peluches.buscar_id(id)

        return render_template("peluche_detalle.html", peluche=peluche)
    except Exception:
        flash("Error al cargar detalles.", "danger")
        return redirect(url_for("peluches"))

@app.route("/peluche/editar/<int:id>")
def editar_peluche(id):
    if "id_usuario" not in session:
        return redirect(url_for("inicio"))

    peluche = Peluches.buscar_id(id)
    if not peluche or peluche.donador_id != session["id_usuario"]:
        flash("No tienes permiso.", "danger")
        return redirect(url_for("peluches"))

    return render_template("peluche_form.html", peluche=peluche)

@app.route("/peluche/modificar/<int:id>", methods=["POST"])
def modificar_peluche(id):
    if "id_usuario" not in session:
        return redirect(url_for("inicio"))

    datos = {
        "id_peluche": id,
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "donador_id": session["id_usuario"]
    }

    errores = Peluches.validar(datos)
    if errores:
        for error in errores:
            flash(error, "danger")
        return render_template("peluche_form.html", peluche=datos)

    try:
        Peluches.modificar(datos)
        flash("Registro actualizado.", "success")
        return redirect(url_for("peluches"))
    except Exception:
        flash("Error al actualizar.", "danger")
        return render_template("peluche_form.html", peluche=datos)

@app.route("/peluche/adoptar/<int:id>", methods=["POST"])
def adoptar_peluche(id):
    if "id_usuario" not in session:
        return redirect(url_for("inicio"))

    peluche = Peluches.buscar_id(id)
    if not peluche:
        flash("Peluche no encontrado.", "danger")
    elif peluche.adoptador_id is not None:
        flash("Este peluche ya tiene una familia.", "danger")
    elif peluche.donador_id == session["id_usuario"]:
        flash("No puedes adoptar tu propio peluche.", "danger")
    else:
        Peluches.adoptar({"id_peluche": id, "adoptador_id": session["id_usuario"]})
        flash("¡Felicidades! Has adoptado un nuevo amigo.", "success")
        
    return redirect(url_for("peluches"))

@app.route("/peluche/confirmar_eliminar/<int:id>")
def confirmar_eliminar_peluche(id):
    if "id_usuario" not in session:
        return redirect(url_for("inicio"))

    peluche = Peluches.buscar_id(id)
    if not peluche or peluche.donador_id != session["id_usuario"]:
        flash("No tienes permiso.", "danger")
        return redirect(url_for("peluches"))

    return render_template(
        "confirmar_eliminar.html",
        mensaje=f"Vas a eliminar '{peluche.nombre}'. Esta acción no se puede deshacer.",
        accion=url_for("eliminar_peluche", id=id)
    )

@app.route("/peluche/eliminar/<int:id>")
def eliminar_peluche(id):
    if "id_usuario" not in session:
        return redirect(url_for("inicio"))

    try:
        Peluches.eliminar(id, session["id_usuario"])
        flash("Peluche eliminado correctamente.", "success")
    except Exception:
        flash("Error al intentar eliminar.", "danger")

    return redirect(url_for("peluches"))