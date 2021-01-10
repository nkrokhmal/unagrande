from flask import url_for, render_template, flash, request, make_response, current_app, request
from werkzeug.utils import redirect
from . import main
from .errors import bad_request
from .. import db
from .forms import SKUForm
from ..models import SKU, Boiling
from sqlalchemy import or_, and_
from flask_restplus import reqparse


@main.route('/add_sku', methods=['POST', 'GET'])
def add_sku():
    form = SKUForm()
    name = request.args.get('name')
    if form.validate_on_submit():
        # todo: check if boiling does not exist
        sku = SKU(
            name=form.name.data,
            brand_name=form.brand_name.data,
            weight_netto=form.weight_netto.data,
            weight_form_factor=form.weight_form_factor.data,
            output_per_ton=form.output_per_ton.data,
            shelf_life=form.shelf_life.data,
            packing_speed=form.packing_speed.data,
            packing_reconfiguration=form.packing_reconfiguration.data,
            packing_reconfiguration_format=form.packing_reconfiguration_format.data
        )
        boiling = [x for x in form.boilings if
                   x.percent == dict(form.percent.choices).get(form.percent.data) and
                   x.is_lactose == dict(form.is_lactose.choices).get(form.is_lactose.data) and
                   x.ferment == dict(form.ferment.choices).get(form.ferment.data)][0]
        sku.boilings.append(boiling)

        if form.form_factor.data != -1:
            sku.form_factor_id = [x.id for x in form.form_factors if
                                  x.name == dict(form.form_factor.choices).get(form.form_factor.data)][0]

        if form.packer.data != -1:
            sku.packer_id = [x.id for x in form.packers if
                             x.name == dict(form.packer.choices).get(form.packer.data)][0]

        if form.pack_type.data != -1:
            sku.pack_type_id = [x.id for x in form.pack_types if
                                x.name == dict(form.pack_type.choices).get(form.pack_type.data)][0]

        db.session.add(sku)
        try:
            db.session.commit()
            flash('SKU успешно добавлено')
        except Exception as e:
            flash('Exception occurred in get_sku request. Error: {}.'.format(e), 'error')
            db.session.rollback()
        return redirect(url_for('.get_sku'))
    if name:
        form.name.data = name
    return render_template('add_sku.html', form=form)


@main.route('/get_sku', methods=['GET'])
def get_sku():
    form = SKUForm()
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(SKU) \
        .order_by(SKU.name) \
        .paginate(
        page, per_page=current_app.config['SKU_PER_PAGE'],
        error_out=False
    )
    skus = pagination.items
    return render_template('get_sku.html', form=form, skus=skus, paginations=pagination, endopoints='.get_sku')


@main.route('/edit_sku/<int:sku_id>', methods=['GET', 'POST'])
def edit_sku(sku_id):
    form = SKUForm()
    sku = db.session.query(SKU).get_or_404(sku_id)
    if form.validate_on_submit() and sku is not None:
        sku.name = form.name.data
        sku.brand_name = form.brand_name.data
        sku.weight_netto = form.weight_netto.data
        sku.weight_form_factor = form.weight_form_factor.data
        sku.output_per_ton = form.output_per_ton.data
        sku.shelf_life = form.shelf_life.data
        sku.packing_speed = form.packing_speed.data
        sku.packing_reconfiguration = form.packing_reconfiguration.data
        sku.packing_reconfiguration_format = form.packing_reconfiguration_format.data

        boiling = [x for x in form.boilings if
                   x.percent == dict(form.percent.choices).get(form.percent.data) and
                   x.is_lactose == dict(form.is_lactose.choices).get(form.is_lactose.data) and
                   x.ferment == dict(form.ferment.choices).get(form.ferment.data)][0]
        sku.boilings.append(boiling)

        if form.form_factor.data != -1:
            sku.form_factor_id = [x.id for x in form.form_factors if
                                  x.name == dict(form.form_factor.choices).get(form.form_factor.data)][0]

        if form.packer.data != -1:
            sku.packer_id = [x.id for x in form.packers if
                             x.name == dict(form.packer.choices).get(form.packer.data)][0]
        if form.pack_type.data != -1:
            sku.pack_type_id = [x.id for x in form.pack_types if
                                x.name == dict(form.pack_type.choices).get(form.pack_type.data)][0]
        db.session.commit()
        flash('SKU успешно изменено')
        return redirect(url_for('.get_sku'))

    if len(sku.boilings) > 0:
        generate_default_value(form.percent, sku.boilings[0].percent)
        generate_default_value(form.is_lactose, sku.boilings[0].is_lactose)
        generate_default_value(form.ferment, sku.boilings[0].ferment)

    if sku.pack_types is not None:
        generate_default_value(form.pack_type, sku.pack_types.name)

    if sku.packer is not None:
        generate_default_value(form.packer, sku.packer.name)

    if sku.form_factor is not None:
        generate_default_value(form.form_factor, sku.form_factor.name)

    form.process()

    form.name.data = sku.name
    form.brand_name.data = sku.brand_name
    form.weight_netto.data = sku.weight_netto
    form.weight_form_factor.data = sku.weight_form_factor
    form.output_per_ton.data = sku.output_per_ton
    form.shelf_life.data = sku.shelf_life
    form.packing_speed.data = sku.packing_speed
    form.packing_reconfiguration.data = sku.packing_reconfiguration
    form.packing_reconfiguration_format.data = sku.packing_reconfiguration_format

    return render_template('edit_sku.html', form=form)


@main.route('/delete_sku/<int:sku_id>', methods=['DELETE'])
def delete_sku(sku_id):
    sku = db.session.query(SKU).get_or_404(sku_id)
    if sku:
        for boiling in sku.boilings:
            sku.boilings.remove(boiling)
        db.session.commit()
        db.session.delete(sku)
        db.session.commit()
        flash('SKU успешно удалено')
    return redirect(url_for('.get_sku'))


def generate_default_value(form, val):
    for key, value in dict(form.choices).items():
        if value == val:
            form.default = key
