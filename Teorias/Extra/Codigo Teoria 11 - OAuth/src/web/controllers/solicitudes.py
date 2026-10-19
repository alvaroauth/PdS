"""Recurso protegido: requiere sesión para ver y permiso local para aprobar."""

from flask import Blueprint, abort, current_app, flash, redirect, render_template, session, url_for

from src.core import permisos, solicitudes
from src.web.auth import login_requerido

bp = Blueprint("solicitudes", __name__, url_prefix="/solicitudes")


def _puede_aprobar():
    return permisos.puede_aprobar(session["usuario"], current_app.config["JEFES_DE_SERVICIO"])


@bp.get("")
@login_requerido
def index():
    return render_template(
        "solicitudes/index.html",
        solicitudes=solicitudes.listar(),
        puede_aprobar=_puede_aprobar(),
    )


@bp.post("/<int:solicitud_id>/aprobar")
@login_requerido
def aprobar(solicitud_id):
    # Autenticado no implica autorizado: el ingreso con el proveedor no da este permiso.
    if not _puede_aprobar():
        abort(403)
    try:
        solicitudes.aprobar(solicitud_id)
    except solicitudes.SolicitudInexistente:
        abort(404)
    flash(f"Solicitud {solicitud_id} aprobada.")
    return redirect(url_for("solicitudes.index"))
