"""Pruebas sin red: se reemplaza el canje con el proveedor por un token simulado."""

import base64
import copy
import json

import pytest
from authlib.integrations.flask_client import OAuthError
from cachelib import SimpleCache

from src.core import solicitudes
from src.web import create_app
from src.web.auth import SCOPE_CALENDARIO, oauth

ISS = "https://accounts.google.com"
JEFE = f"{ISS}|jefe-123"


def _jwt_falso(claims):
    def parte(datos):
        return base64.urlsafe_b64encode(json.dumps(datos).encode()).rstrip(b"=").decode()

    return f"{parte({'alg': 'RS256', 'kid': 'k1'})}.{parte(claims)}.firma"


def _token(sub, scope="openid email profile " + SCOPE_CALENDARIO):
    claims = {"iss": ISS, "sub": sub, "aud": "cliente", "name": f"Persona {sub}", "email": "x@example.com"}
    return {"access_token": "ya29.opaco-de-prueba", "token_type": "Bearer", "id_token": _jwt_falso(claims), "scope": scope, "userinfo": claims}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(solicitudes, "_SOLICITUDES", copy.deepcopy(solicitudes._SOLICITUDES))
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "OIDC_CLIENT_ID": "cliente",
            "OIDC_CLIENT_SECRET": "secreto",
            "JEFES_DE_SERVICIO": {JEFE},
            "SESSION_CACHELIB": SimpleCache(),
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()


def _ingresar(client, monkeypatch, sub, **kwargs):
    monkeypatch.setattr(oauth.proveedor, "authorize_access_token", lambda: _token(sub, **kwargs))
    return client.get("/auth/callback?code=c&state=s")


def test_sin_sesion_no_accede_a_solicitudes(client):
    respuesta = client.get("/solicitudes")
    assert respuesta.status_code == 302
    assert respuesta.location == "/"


def test_callback_crea_sesion_propia(client, monkeypatch):
    respuesta = _ingresar(client, monkeypatch, "persona-1")
    assert respuesta.status_code == 302
    assert respuesta.location == "/solicitudes"
    with client.session_transaction() as sesion:
        assert sesion["usuario"]["sub"] == "persona-1"
        assert sesion["access_token"]["access_token"] == "ya29.opaco-de-prueba"
    # La cookie sólo lleva el identificador de la sesión del servidor.
    cookie = client.get_cookie("session").value
    assert "ya29" not in cookie and "persona-1" not in cookie
    assert b"Persona persona-1" in client.get("/solicitudes").data


def test_perfil_muestra_header_y_clave_identidad(client, monkeypatch):
    _ingresar(client, monkeypatch, "persona-1")
    html = client.get("/auth/perfil").get_data(as_text=True)
    assert "RS256" in html
    assert f"{ISS}|persona-1" in html


def test_cancelar_en_google_vuelve_al_inicio_sin_sesion(client):
    # Sin simular: Authlib lee ?error=access_denied y lanza OAuthError.
    respuesta = client.get("/auth/callback?error=access_denied&state=s")
    assert respuesta.status_code == 302 and respuesta.location == "/"
    with client.session_transaction() as sesion:
        assert "usuario" not in sesion
    assert "Cancelaste el ingreso" in client.get("/").get_data(as_text=True)


def test_canje_rechazado_responde_400(client, monkeypatch):
    def falla():
        raise OAuthError(error="invalid_grant", description="Invalid code verifier.")

    monkeypatch.setattr(oauth.proveedor, "authorize_access_token", falla)
    respuesta = client.get("/auth/callback?code=c&state=s")
    assert respuesta.status_code == 400
    with client.session_transaction() as sesion:
        assert "usuario" not in sesion


def test_autenticado_sin_permiso_recibe_403(client, monkeypatch):
    _ingresar(client, monkeypatch, "persona-1")
    assert client.post("/solicitudes/1/aprobar").status_code == 403
    assert solicitudes.listar()[0]["estado"] == "pendiente"


def test_jefe_puede_aprobar(client, monkeypatch):
    _ingresar(client, monkeypatch, "jefe-123")
    assert client.post("/solicitudes/1/aprobar").status_code == 302
    assert solicitudes.listar()[0]["estado"] == "aprobada"
    assert client.post("/solicitudes/99/aprobar").status_code == 404


def test_logout_borra_la_sesion(client, monkeypatch):
    _ingresar(client, monkeypatch, "persona-1")
    client.post("/auth/logout")
    assert client.get("/solicitudes").status_code == 302


def test_login_redirige_al_proveedor_con_parametros_oidc(client, monkeypatch):
    metadata = {
        "issuer": ISS,
        "authorization_endpoint": "https://proveedor.example/authorize",
        "token_endpoint": "https://proveedor.example/token",
        "jwks_uri": "https://proveedor.example/jwks",
    }
    monkeypatch.setattr(oauth.proveedor, "load_server_metadata", lambda: metadata)
    respuesta = client.get("/auth/login")
    assert respuesta.status_code == 302
    url = respuesta.location
    assert url.startswith("https://proveedor.example/authorize?")
    for esperado in [
        "response_type=code",
        "client_id=cliente",
        "redirect_uri=http%3A%2F%2Flocalhost%2Fauth%2Fcallback",
        "scope=openid+email+profile",
        "state=",
        "nonce=",
        "code_challenge=",
        "code_challenge_method=S256",
        "prompt=consent",
    ]:
        assert esperado in url


class _RespuestaFalsa:
    def __init__(self, status_code, datos):
        self.status_code = status_code
        self._datos = datos

    def json(self):
        return self._datos


def test_agenda_usa_el_access_token_como_bearer(client, monkeypatch):
    _ingresar(client, monkeypatch, "persona-1")
    llamadas = []

    def get_falso(url, token, params):
        llamadas.append((url, token))
        return _RespuestaFalsa(200, {"items": [{"summary": "Guardia", "start": {"date": "2026-10-20"}}]})

    monkeypatch.setattr(oauth.proveedor, "get", get_falso)
    html = client.get("/agenda").get_data(as_text=True)
    assert "Guardia" in html
    assert "Authorization: Bearer ya29.opac" in html
    assert llamadas[0][1]["access_token"] == "ya29.opaco-de-prueba"


def test_agenda_respeta_scope_no_otorgado(client, monkeypatch):
    _ingresar(client, monkeypatch, "persona-1", scope="openid email profile")
    monkeypatch.setattr(oauth.proveedor, "get", lambda *a, **k: pytest.fail("no debe llamar a la API"))
    assert "No otorgaste" in client.get("/agenda").get_data(as_text=True)


def test_agenda_con_token_vencido_vuelve_a_ingresar(client, monkeypatch):
    _ingresar(client, monkeypatch, "persona-1")
    monkeypatch.setattr(oauth.proveedor, "get", lambda *a, **k: _RespuestaFalsa(401, {}))
    assert client.get("/agenda").location == "/"


def test_logout_descarta_el_access_token(client, monkeypatch):
    _ingresar(client, monkeypatch, "persona-1")
    client.post("/auth/logout")
    with client.session_transaction() as sesion:
        assert "access_token" not in sesion and "usuario" not in sesion


def test_callback_con_state_desconocido_se_rechaza(client):
    # Sin simular: Authlib no encuentra ese state en la sesión y no llega a la red.
    respuesta = client.get("/auth/callback?code=c&state=no-existe")
    assert respuesta.status_code == 400
    assert b"mismatching_state" in respuesta.data


def _flujo_con_id_token(client, monkeypatch, aud):
    """Login real (state, nonce y PKCE en la sesión) con un Google simulado que
    devuelve un ID token firmado con RS256 y el `aud` indicado."""
    from authlib.jose import JsonWebKey, jwt
    from urllib.parse import parse_qs, urlparse

    clave = JsonWebKey.generate_key("RSA", 2048, is_private=True)
    clave_publica = clave.as_dict(is_private=False) | {"kid": "k1", "use": "sig", "alg": "RS256"}
    metadata = {
        "issuer": ISS,
        "authorization_endpoint": "https://proveedor.example/authorize",
        "token_endpoint": "https://proveedor.example/token",
        "jwks_uri": "https://proveedor.example/jwks",
        "id_token_signing_alg_values_supported": ["RS256"],
    }
    monkeypatch.setattr(oauth.proveedor, "load_server_metadata", lambda: metadata)
    monkeypatch.setattr(oauth.proveedor, "fetch_jwk_set", lambda force=False: {"keys": [clave_publica]})

    url = client.get("/auth/login").location
    state = parse_qs(urlparse(url).query)["state"][0]
    nonce = parse_qs(urlparse(url).query)["nonce"][0]

    import time
    claims = {"iss": ISS, "sub": "persona-1", "aud": aud, "iat": int(time.time()),
              "exp": int(time.time()) + 300, "nonce": nonce}
    id_token = jwt.encode({"alg": "RS256", "kid": "k1"}, claims, clave).decode()
    respuesta_google = {"access_token": "ya29.x", "token_type": "Bearer", "id_token": id_token, "scope": "openid"}
    monkeypatch.setattr(oauth.proveedor, "fetch_access_token", lambda **kwargs: dict(respuesta_google))
    return client.get(f"/auth/callback?code=c&state={state}")


def test_id_token_valido_inicia_sesion(client, monkeypatch):
    respuesta = _flujo_con_id_token(client, monkeypatch, aud="cliente")
    assert respuesta.status_code == 302 and respuesta.location == "/solicitudes"


def test_id_token_con_aud_ajena_se_rechaza(client, monkeypatch):
    respuesta = _flujo_con_id_token(client, monkeypatch, aud="otra-app")
    assert respuesta.status_code == 400
    with client.session_transaction() as sesion:
        assert "usuario" not in sesion
