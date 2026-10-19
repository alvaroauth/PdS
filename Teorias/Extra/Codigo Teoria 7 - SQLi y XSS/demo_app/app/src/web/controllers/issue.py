from flask import Blueprint
from flask import render_template
from src.core import board

issue_blueprint = Blueprint("issues", __name__, url_prefix="/consultas")


@issue_blueprint.route("/")
def index():
    issues = board.list_issues()
    return render_template("issues/index.html", issues=issues)


@issue_blueprint.route("/nuevo")
def new():
    return render_template("issues/new.html")
