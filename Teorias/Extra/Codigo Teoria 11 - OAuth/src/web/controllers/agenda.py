"""Acceso delegado: la app lee el calendario de la persona con su access token."""

from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, url_for

from src.web.auth import SCOPE_CALENDARIO, access_token_actual, login_requerido, oauth

bp = Blueprint("agenda", __name__, url_prefix="/agenda")

# Recurso protegido de OTRA API (Google Calendar), no de nuestra app.
EVENTOS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"


@bp.get("")
@login_requerido
def index():
    token = access_token_actual()
    if token is None:
        flash("No hay access token en el servidor (¿se reinició?). Ingresá de nuevo.")
        return redirect(url_for("inicio"))
    if SCOPE_CALENDARIO not in token["scope"].split():
        # La persona destildó el permiso en la pantalla de consentimiento.
        return render_template("agenda.html", otorgado=False)

    # Authlib agrega la cabecera:  Authorization: Bearer <access_token>
    respuesta = oauth.proveedor.get(
        EVENTOS_URL,
        token=token,
        params={
            "timeMin": datetime.now(timezone.utc).isoformat(),
            "maxResults": 5,
            "singleEvents": "true",
            "orderBy": "startTime",
        },
    )
    if respuesta.status_code == 401:
        flash("El access token venció o fue revocado. Ingresá de nuevo.")
        return redirect(url_for("inicio"))
    datos = respuesta.json()
    return render_template(
        "agenda.html",
        otorgado=True,
        status=respuesta.status_code,
        eventos=datos.get("items", []),
        error=datos.get("error", {}).get("message"),
        bearer=token["access_token"][:10] + "…",
        url=EVENTOS_URL,
    )
