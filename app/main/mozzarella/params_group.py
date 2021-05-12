from app.imports.runtime import *

from app.main import main
from app.models import Group


@main.route("/mozzarella/get_group", methods=["GET", "POST"])
def get_group():
    groups = db.session.query(Group).all()
    return render_template(
        "mozzarella/get_group.html", groups=groups, endpoints=".get_group"
    )
