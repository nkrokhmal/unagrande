from app.imports.runtime import *
from app.main import main


@main.route("/")
def index():
    return render_template("index.html")
