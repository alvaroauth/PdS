# 8 — Ingreso con OpenID Connect en Flask

Ejemplo independiente de la clase de identidad y acceso 2026 (OAuth 2.0, OIDC y JWT).
Una app Flask con **login, logout, una página protegida de solicitudes, un permiso
local para aprobarlas y una página que lee el calendario de la persona con su access
token**. Usa Authlib y Google como proveedor OIDC.

**Sólo para demostración local con datos ficticios.** Las solicitudes están en memoria
(se reinician con el servidor) y no hay base de datos ni usuarios locales persistentes.

## 1. Registrar el cliente en Google (antes de clase)

En <https://console.cloud.google.com/> → **Google Auth Platform** (APIs y servicios →
Credenciales / Pantalla de consentimiento, según la versión de la consola):

1. Crear o elegir un proyecto.
2. **Branding / pantalla de consentimiento**: nombre de la app, email de soporte.
   Es lo que la persona verá en la ventana de autorización.
3. **Audience**: tipo *External*, estado *Testing*. Agregar como **test users** las
   cuentas que van a ingresar (en *Testing* sólo ingresan esas cuentas).
4. **Data access**: los scopes `openid`, `.../auth/userinfo.email`,
   `.../auth/userinfo.profile` y `.../auth/calendar.readonly`.
   En estado *Testing* no hace falta que Google verifique la app; al ingresar
   aparece la advertencia «Google no verificó esta app» → *Continuar*.
5. **APIs y servicios → Biblioteca**: habilitar **Google Calendar API**
   (sólo para la página `/agenda`; con `OIDC_PEDIR_CALENDARIO=0` no hace falta).
6. **Clients → Create client → Web application**:
   - *Authorized redirect URIs*: `http://127.0.0.1:5004/auth/callback`
7. Copiar el **Client ID** y el **Client secret**.

La URI de retorno se compara **exactamente**: usar siempre `127.0.0.1` (no `localhost`)
y el puerto 5004. Si no coinciden, Google responde `redirect_uri_mismatch`, que es
justamente un buen error para mostrar en clase.

## 2. Ejecutar

Requisitos: Python 3.12 o superior y Poetry. Desde esta carpeta:

```bash
cp .env.example .env   # completar SECRET_KEY, OIDC_CLIENT_ID y OIDC_CLIENT_SECRET
poetry install
poetry run flask --app src.web:create_app run --host 127.0.0.1 --port 5004
```

Abrir <http://127.0.0.1:5004/>.

## 3. Recorrido docente

| Paso | Qué hacer | Qué se observa |
|---|---|---|
| 1 | Abrir `/solicitudes` sin sesión | Redirige al inicio: no accede |
| 2 | “Ingresar con Google” | En la terminal se imprime la URL de autorización |
| 3 | Leer esa URL | `response_type=code`, `client_id`, `redirect_uri`, `scope`, `state`, `nonce`, `code_challenge` |
| 4 | Elegir cuenta | **Pantalla de consentimiento**: nombre de la app, datos de identidad y la casilla «Ver tus calendarios» |
| 5 | Aceptar | Vuelve a `/auth/callback?code=...&state=...` y luego a `/solicitudes` |
| 6 | Abrir “Perfil e ID token” | Header y claims del JWT, scopes otorgados, clave `iss|sub` |
| 7 | Abrir “Agenda (access token)” | La app llama a Google Calendar con `Authorization: Bearer ...` |
| 8 | Intentar “Aprobar” | **403**: autenticado no implica autorizado |
| 9 | Copiar `iss|sub` en `JEFES_DE_SERVICIO` del `.env` y reiniciar | Ahora sí aprueba (volver a ingresar si la sesión venció) |
| 10 | “Cerrar sesión” | Vuelve al inicio; `/solicitudes` ya no es accesible |
| 11 | Ingresar y **destildar** el calendario | `/agenda` informa que no hay permiso y no llama a la API |
| 12 | Ingresar y **cancelar** en el consentimiento | Vuelve al inicio con «Cancelaste el ingreso» (no es un error) |

En DevTools, abrir la pestaña Network con **Preserve log** antes del paso 2 permite
ver las redirecciones (`/auth/login` → Google → `/auth/callback`) que pasan muy rápido.

Después del paso 10 se vuelve a ingresar sin escribir la contraseña: **cerramos la sesión
de la app, no la de Google**. Es una buena pregunta para la clase.

`OIDC_FORZAR_CONSENTIMIENTO=1` agrega `prompt=consent`, para que Google muestre la
ventana de autorización en cada ingreso y no sólo la primera vez.

Variante del paso 3: cambiar `state` en la URL del callback antes de que el navegador
la siga (o recargar el callback ya usado) produce un rechazo: el `state` no corresponde
a ningún intento guardado en la sesión.

## 4. Recorrido por el código

| Concepto de la clase | Dónde está |
|---|---|
| Configuración del cliente: discovery, `client_id`, `client_secret` | `src/web/auth.py` → `init_oauth`; valores en `.env` |
| Scopes solicitados (`openid email profile` + calendario) | `src/web/auth.py` → `SCOPES`, `SCOPE_CALENDARIO` |
| URL de callback (`redirect_uri`) | `src/web/auth.py` → `login` (`url_for("auth.callback", _external=True)`) |
| PKCE S256 | `client_kwargs={"code_challenge_method": "S256"}` |
| `state`, `nonce`, canje del código, validación del ID token | `authorize_redirect` / `authorize_access_token` (Authlib) |
| Sesión propia de la app (del lado del servidor) | `callback`: `session["usuario"]`; Flask-Session en `src/web/__init__.py` |
| Logout | `logout`: `session.clear()` |
| Página protegida | `src/web/controllers/solicitudes.py` + `login_requerido` |
| Usar el access token (Bearer) ante otra API | `src/web/controllers/agenda.py` |
| Permiso local por `(iss, sub)` | `src/core/permisos.py` → `puede_aprobar` |
| Factory y registro de Blueprints | `src/web/__init__.py` |

Flujo:

```text
GET /auth/login
  → authorize_redirect: guarda state, nonce y code_verifier en la sesión
  → 302 al authorization_endpoint del proveedor
Proveedor: autentica + pantalla de consentimiento
  → 302 a /auth/callback?code=...&state=...
GET /auth/callback
  → authorize_access_token: verifica state, canjea code + code_verifier,
    valida el ID token (firma, iss, aud, exp, nonce)
  → session["usuario"] = {iss, sub, ...} → 302 /solicitudes
GET /agenda
  → GET googleapis.com/calendar/...  Authorization: Bearer <access_token>
POST /solicitudes/<id>/aprobar
  → login_requerido → puede_aprobar(iss|sub) ? aprobar : 403
```

Qué **no** hace la app, a propósito:

- No recibe ni guarda contraseñas.
- No pone datos en la cookie: la sesión vive en el servidor (Flask-Session) y el
  navegador sólo recibe un identificador.
- No acepta el access token de Google como credencial de su propia API.
- No usa el email como clave: vincula por `(iss, sub)`.
- No interpreta los scopes como permisos del hospital.

**Sesión del lado del servidor.** Por defecto, Flask guarda la sesión en una cookie
**firmada, no cifrada**: su contenido es legible en el navegador. Como en la clase de
sesiones, el ejemplo usa **Flask-Session**: los datos (usuario, access token, y durante
el login el `state`, el `nonce` y el verificador de PKCE) quedan en archivos de
`instance/sesiones/`, y la cookie sólo lleva un identificador. Para la demo la sesión
también guarda el header y los claims del ID token (página de perfil). En producción se
usaría Redis o una base de datos en lugar de archivos.

## 5. Pruebas automatizadas (sin red)

```bash
poetry run pytest -q
```

Simulan el proveedor: sin sesión no hay acceso, el callback crea la sesión,
un callback rechazado no la crea, 403 sin permiso, aprobación con permiso, logout
la URL de autorización con todos los parámetros OIDC y PKCE, la llamada Bearer a
Calendar, el scope no otorgado, el token vencido (401) y un login completo con un ID
token firmado de verdad: válido inicia sesión; con `aud` ajena se rechaza con 400.

## Otros proveedores

Cualquier proveedor OIDC sirve cambiando `OIDC_DISCOVERY_URL` y las credenciales
(por ejemplo, Keycloak: `http://localhost:8080/realms/<realm>/.well-known/openid-configuration`).
El texto del botón “Ingresar con Google” está en `templates/inicio.html`.

## Alcance deliberado

Sin base de datos, sin alta de usuarios locales, sin roles administrables, sin
logout en el proveedor (Google no ofrece `end_session_endpoint`), sin token CSRF en
los formularios (la cookie usa `SameSite=Lax`) y sin HTTPS. No es una base para producción.
