"""Inicio de sesión con OpenID Connect (Authorization Code + PKCE) usando Authlib.

Authlib resuelve las partes delicadas del protocolo:
  - genera y verifica `state` (y `nonce`);
  - genera el `code_verifier` y envía su huella (PKCE S256);
  - canjea el código en el token endpoint;
  - valida el ID token: firma (con las claves del jwks_uri), iss, aud, exp y nonce.

Nuestra app decide qué hacer con esa identidad: crear SU sesión y aplicar SUS permisos.
"""

import base64
import json
from functools import wraps

from authlib.integrations.flask_client import OAuth, OAuthError
from joserfc.errors import JoseError  # errores al validar el ID token (lo usa Authlib)
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

oauth = OAuth()
bp = Blueprint("auth", __name__, url_prefix="/auth")

# Alcances solicitados al proveedor. Son los que aparecen en la pantalla de consentimiento.
#   openid  → convierte el pedido OAuth en OIDC: recibimos un ID token.
#   email   → claims email y email_verified.
#   profile → claims name, picture, etc.
SCOPES = "openid email profile"

# Acceso delegado a un RECURSO de la persona (OAuth "puro"): leer su calendario.
# Google lo muestra como una casilla aparte que se puede destildar.
SCOPE_CALENDARIO = "https://www.googleapis.com/auth/calendar.readonly"


def init_oauth(app):
    """Registra el cliente OIDC. No hay red aquí: el discovery se descarga al primer uso."""
    scopes = SCOPES
    if app.config["OIDC_PEDIR_CALENDARIO"]:
        scopes += " " + SCOPE_CALENDARIO
    oauth.init_app(app)
    oauth.register(
        name="proveedor",
        # Del documento de descubrimiento salen authorization_endpoint,
        # token_endpoint, jwks_uri e issuer: no los escribimos a mano.
        server_metadata_url=app.config["OIDC_DISCOVERY_URL"],
        client_id=app.config["OIDC_CLIENT_ID"],
        client_secret=app.config["OIDC_CLIENT_SECRET"],
        client_kwargs={"scope": scopes, "code_challenge_method": "S256"},
    )


@bp.get("/login")
def login():
    # URL de callback (redirect_uri): debe coincidir EXACTAMENTE con la registrada
    # en el proveedor. Con el servidor de la demo: http://127.0.0.1:5004/auth/callback
    redirect_uri = url_for("auth.callback", _external=True)
    extra = {"prompt": "consent"} if current_app.config["OIDC_FORZAR_CONSENTIMIENTO"] else {}
    respuesta = oauth.proveedor.authorize_redirect(redirect_uri, **extra)
    # Para mostrar en clase: response_type, client_id, redirect_uri, scope, state,
    # nonce y code_challenge viajan en esta URL hacia el proveedor.
    current_app.logger.warning("Redirigiendo al proveedor:\n%s", respuesta.location)
    return respuesta


@bp.get("/callback")
def callback():
    try:
        token = oauth.proveedor.authorize_access_token()
    except OAuthError as error:
        # `access_denied` es el aviso de OAuth de que la persona dijo que no.
        # No es un error de nuestra app: volvemos al inicio con un mensaje.
        if error.error == "access_denied":
            flash("Cancelaste el ingreso: la app no recibió ningún dato.")
            return redirect(url_for("inicio"))
        # `state` que no coincide o canje rechazado: el callback no es válido.
        return _callback_invalido(error)
    except JoseError as error:
        # ID token inválido (firma, iss, aud, exp, nonce): tampoco es válido.
        return _callback_invalido(error)

    # `userinfo` contiene los claims del ID token, YA validados por Authlib.
    claims = token["userinfo"]

    # Sesión propia de la app. Vive en el servidor (Flask-Session): la cookie
    # del navegador sólo lleva un identificador, nunca estos datos.
    session.clear()
    session["usuario"] = {
        "iss": claims["iss"],
        "sub": claims["sub"],
        "nombre": claims.get("name"),
        "email": claims.get("email"),
    }
    # El access token también queda en la sesión del servidor, para /agenda.
    session["access_token"] = {
        "access_token": token["access_token"],
        "token_type": token.get("token_type", "Bearer"),
        "scope": token.get("scope", ""),
    }
    # Sólo para la página /perfil de la demo.
    session["id_token"] = {
        "header": _decodificar_parte(token["id_token"], 0),
        "claims": dict(claims),
        "scope_otorgado": token.get("scope"),
    }
    flash(f"Ingresaste como {claims.get('name') or claims['sub']}.")
    return redirect(url_for("solicitudes.index"))


@bp.post("/logout")
def logout():
    # Cierra la sesión de ESTA app. La sesión en el proveedor sigue abierta.
    session.clear()
    flash("Cerraste la sesión en la aplicación.")
    return redirect(url_for("inicio"))


@bp.get("/perfil")
def perfil():
    if "usuario" not in session:
        return redirect(url_for("inicio"))
    return render_template("perfil.html", id_token=session["id_token"])


def _callback_invalido(error):
    """El intento de login está roto o manipulado: 400 (Bad Request)."""
    current_app.logger.warning("Callback rechazado: %s", error)
    return render_template("error.html", error=error), 400


def login_requerido(vista):
    """Sin sesión de la app no se accede: se vuelve al inicio para ingresar."""

    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            flash("Ingresá para ver las solicitudes.")
            return redirect(url_for("inicio"))
        return vista(*args, **kwargs)

    return envoltura


def access_token_actual():
    """Access token guardado en la sesión del servidor, o None."""
    return session.get("access_token")


def _decodificar_parte(jwt, indice):
    """Decodifica (NO verifica) una parte del JWT, sólo para mostrarla."""
    parte = jwt.split(".")[indice]
    return json.loads(base64.urlsafe_b64decode(parte + "=" * (-len(parte) % 4)))
