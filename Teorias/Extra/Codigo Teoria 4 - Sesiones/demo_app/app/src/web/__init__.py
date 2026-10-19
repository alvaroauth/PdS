from flask import Flask, render_template, request, make_response, session
from flask_session import Session

from src.core import board
from src.core import database
from src.core import seeds
from src.web.config import config
from src.web.helpers import handler
from src.web.helpers import auth
from src.web.controllers.issue import issue_blueprint
from src.web.controllers.users import user_blueprint
from src.web.controllers.auth import auth_blueprint

import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


def create_app(env="development", static_folder="static"):
    app = Flask(__name__, static_folder=static_folder)

    # Import config
    app.config.from_object(config[env])

    # Server Side session - si está comentado usa sesiones en cookies
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    app.config['SESSION_COOKIE_SECURE'] = False  # True si es https
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    # Configure db
    db = database.init_app(app)

    # Define home
    @app.route("/")
    def home():
        # Obtener el valor actual del contador desde la cookie
        contador_actual = request.cookies.get('contador_visitas')
        # Si no existe la cookie, inicializar en 0
        if contador_actual is None:
            nuevo_contador = 1
        else:
            # Convertir a entero y sumar 1
            nuevo_contador = int(contador_actual) + 1
        # Crear la respuesta
        response = make_response(render_template("home.html", visitas=nuevo_contador))
        # Actualizar la cookie con el nuevo valor
        response.set_cookie('contador_visitas', str(nuevo_contador), httponly = False) # httponly = False para que sea accesible desde JavaScript

        #if session.get("pos_equipos") is None:
        #    session["pos_equipos"] = { "A" : "Campeón", "B": "Sub Campeón",
        #                        "C": "Semi finalista", "D": "Semi finalista"}

        return response

    # Load blueprints
    app.register_blueprint(issue_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint)

    # Error handlers
    app.register_error_handler(404, handler.not_found_error)
    app.register_error_handler(500, handler.generic_error)
    app.register_error_handler(401, handler.unauthorized)

    # Add to jinja
    app.jinja_env.globals.update(is_authenticated=auth.is_authenticated)

    # Commands
    @app.cli.command(name="resetdb")
    def resetdb():
        """Elimino y creo la base de datos."""
        database.init_db()

    @app.cli.command(name="seeds")
    def seedsdb():
        seeds.run()


    #SQLi
    def login_sqli():
        return render_template('auth/login_sqli.html')
    app.add_url_rule("/iniciar_sesion_sqli", 'auth_login_sqli', login_sqli)
    
    #app.add_url_rule(
    #    "/autenticacion_sqli", 'auth_authenticate_sqli', auth.authenticate_sqli, methods=['POST']
    #)
    
    # XSS
    app.add_url_rule("/ejemplo_xss", 'musician_xss', board.find_musician_xss)

    # Ajax
    def ajax():
        return render_template('ajax.html')
    app.add_url_rule("/ejemplo_ajax","ejemplo_ajax",ajax)

    # Ajax jquery
    def ajax_jquery():
        return render_template('ajax_jquery.html')
    app.add_url_rule("/ejemplo_ajax_jquery","ejemplo_ajax_jquery",ajax_jquery)

    # Ajax fetch
    def ajax_fetch():
        return render_template('ajax_fetch.html')
    app.add_url_rule("/ejemplo_ajax_fetch","ejemplo_ajax_fetch",ajax_fetch)

    # Ajax async/await
    def ajax_async_await():
        return render_template('ajax_async_await.html')
    app.add_url_rule("/ejemplo_ajax_async_await","ejemplo_ajax_async_await",ajax_async_await)

    app.add_url_rule("/musicos", 'musician_ajax', board.find_musician_by_name)
    app.add_url_rule("/all_musicos", 'all_musician_ajax', board.list_musicians)
    
    return app
