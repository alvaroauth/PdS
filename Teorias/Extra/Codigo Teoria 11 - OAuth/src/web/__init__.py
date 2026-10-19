"""Factory: configuración, cliente OIDC y Blueprints."""

import os
from pathlib import Path

from cachelib import FileSystemCache
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_session import Session


def create_app(test_config=None):
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        OIDC_DISCOVERY_URL=os.getenv(
            "OIDC_DISCOVERY_URL",
            "https://accounts.google.com/.well-known/openid-configuration",
        ),
        OIDC_CLIENT_ID=os.getenv("OIDC_CLIENT_ID"),
        OIDC_CLIENT_SECRET=os.getenv("OIDC_CLIENT_SECRET"),
        OIDC_FORZAR_CONSENTIMIENTO=os.getenv("OIDC_FORZAR_CONSENTIMIENTO", "1") == "1",
        OIDC_PEDIR_CALENDARIO=os.getenv("OIDC_PEDIR_CALENDARIO", "1") == "1",
        JEFES_DE_SERVICIO={
            j.strip() for j in os.getenv("JEFES_DE_SERVICIO", "").split(",") if j.strip()
        },
        # Sesión del lado del servidor (como en la clase de sesiones): los datos
        # quedan en archivos de instance/sesiones; la cookie sólo lleva el id.
        SESSION_TYPE="cachelib",
        SESSION_CACHELIB=FileSystemCache(
            str(Path(__file__).resolve().parents[2] / "instance" / "sesiones"),
            threshold=500,
        ),
        # La cookie de sesión no se envía en POST iniciados desde otros sitios.
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_HTTPONLY=True,
    )
    if test_config:
        app.config.update(test_config)
    for clave in ("SECRET_KEY", "OIDC_CLIENT_ID", "OIDC_CLIENT_SECRET"):
        if not app.config.get(clave):
            raise RuntimeError(f"Falta {clave}. Copiá .env.example a .env y completalo.")

    from src.web.auth import bp as auth_bp
    from src.web.auth import init_oauth
    from src.web.controllers.agenda import bp as agenda_bp
    from src.web.controllers.solicitudes import bp as solicitudes_bp

    Session(app)
    init_oauth(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(solicitudes_bp)
    app.register_blueprint(agenda_bp)

    @app.get("/")
    def inicio():
        return render_template("inicio.html")

    @app.errorhandler(403)
    def prohibido(error):
        return render_template("403.html"), 403

    return app
