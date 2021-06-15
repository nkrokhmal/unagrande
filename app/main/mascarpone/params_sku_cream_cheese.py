from app.imports.runtime import *

from werkzeug.utils import redirect

from app.main import main
from app.globals import db
from app.models import CreamCheeseSKU, CreamCheeseLine, Group
from app.enum import LineName
from app.utils.features.form_utils import *


from .forms import SKUCreamCheeseForm


@main.route("/mascarpone/add_sku_cream_cheese", methods=["POST", "GET"])
@flask_login.login_required
def mascarpone_add_sku_cream_cheese():
    form = SKUCreamCheeseForm()
    name = flask.request.args.get("name")
    if form.validate_on_submit():
        sku = CreamCheeseSKU(
            name=form.name.data,
            brand_name=form.brand_name.data,
            weight_netto=form.weight_netto.data,
            shelf_life=form.shelf_life.data,
            packing_speed=form.packing_speed.data,
            collecting_speed=form.packing_speed.data,
            in_box=form.in_box.data,
        )
        sku = fill_mascarpone_sku_from_form(sku, form)
        mascarpone_line = (
            db.session.query(CreamCheeseLine)
            .filter(CreamCheeseLine.name == LineName.MASCARPONE)
            .first()
        )
        sku.line = mascarpone_line

        db.session.add(sku)
        db.session.commit()
        flask.flash("SKU успешно добавлено", "success")
        return redirect(flask.url_for(".mascarpone_get_sku_cream_cheese", page=1))
    if name:
        form.name.data = name
    return flask.render_template("mascarpone/add_sku_cream_cheese.html", form=form)


@main.route("/mascarpone/get_sku_cream_cheese/<int:page>", methods=["GET"])
@flask_login.login_required
def mascarpone_get_sku_cream_cheese(page):
    flask.session.clear()
    form = SKUCreamCheeseForm()
    skus_count = db.session.query(CreamCheeseSKU).count()

    pagination = (
        db.session.query(CreamCheeseSKU)
        .join(Group)
        .filter(Group.name == "Кремчиз")
        .order_by(CreamCheeseSKU.name)
        .paginate(
            page, per_page=flask.current_app.config["SKU_PER_PAGE"], error_out=False
        )
    )
    return flask.render_template(
        "mascarpone/get_sku_cream_cheese.html",
        form=form,
        pagination=pagination,
        page=page,
        skus_count=skus_count,
        per_page=flask.current_app.config["SKU_PER_PAGE"],
        endopoints=".mascarpone_get_sku_cream_cheese",
    )


@main.route("/mascarpone/edit_sku_cream_cheese/<int:sku_id>", methods=["GET", "POST"])
@flask_login.login_required
def mascarpone_edit_sku_cream_cheese(sku_id):
    form = SKUCreamCheeseForm()
    sku = db.session.query(CreamCheeseSKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        sku.name = form.name.data
        sku.brand_name = form.brand_name.data
        sku.weight_netto = form.weight_netto.data
        sku.shelf_life = form.shelf_life.data
        sku.packing_speed = form.packing_speed.data
        sku.in_box = form.in_box.data
        fill_mascarpone_sku_from_form(sku, form)

        db.session.commit()

        flask.flash("SKU успешно изменено", "success")
        return redirect(flask.url_for(".mascarpone_get_sku_cream_cheese", page=1))

    if len(sku.made_from_boilings) > 0:
        default_form_value(form.boiling, sku.made_from_boilings[0].to_str())

    if sku.group is not None:
        default_form_value(form.group, sku.group.name)

    form.process()

    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.weight_netto.data = sku.weight_netto
    form.shelf_life.data = sku.shelf_life
    form.packing_speed.data = sku.packing_speed
    form.in_box.data = sku.in_box

    return flask.render_template(
        "mascarpone/edit_sku_cream_cheese.html", form=form, sku_id=sku_id
    )


@main.route("/mascarpone/delete_sku_cream_cheese/<int:sku_id>", methods=["DELETE"])
@flask_login.login_required
def mascarpone_delete_sku_cream_cheese(sku_id):
    sku = db.session.query(CreamCheeseSKU).get_or_404(sku_id)
    if sku:
        db.session.delete(sku)
        db.session.commit()
        flask.flash("SKU успешно удалено", "success")
    time.sleep(2.0)
    return redirect(flask.url_for(".mascarpone_get_sku_cream_cheese", page=1))
