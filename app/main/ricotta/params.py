from app.imports.runtime import *
from app.main import main


@main.route("/ricotta_params", methods=["GET"])
def ricotta_params():
    return flask.render_template("ricotta/params.html")
