from .. import db
from sqlalchemy.orm import relationship, backref
from . import SKU, Group, Line, FormFactor, Boiling, BoilingTechnology


class CreamCheeseSKU(SKU):
    __tablename__ = 'cream_cheese_skus'
    __mapper_args__ = {'polymorphic_identity': 'cream_cheese_skus'}

    id = db.Column(db.Integer, db.ForeignKey('skus.id'), primary_key=True)


class CreamCheeseLine(Line):
    __tablename__ = 'cream_cheese_lines'
    __mapper_args__ = {'polymorphic_identity': 'cream_cheese_lines'}

    id = db.Column(db.Integer, db.ForeignKey('lines.id'), primary_key=True)
    params = db.Column(db.String)


class CreamCheeseFormFactor(FormFactor):
    __tablename__ = 'cream_cheese_form_factors'
    __mapper_args__ = {'polymorphic_identity': 'cream_cheese_form_factor'}

    id = db.Column(db.Integer, db.ForeignKey('form_factors.id'), primary_key=True)


class CreamCheeseBoiling(Boiling):
    __tablename__ = 'cream_cheese_boilings'
    __mapper_args__ = {'polymorphic_identity': 'cream_cheese_boiling'}

    id = db.Column(db.Integer, db.ForeignKey('boilings.id'), primary_key=True)
    boiling_type = db.Column(db.String)


class CreamCheeseBoilingTechnology(BoilingTechnology):
    __tablename__ = 'cream_cheese_boiling_technologies'
    __mapper_args__ = {'polymorphic_identity': 'cream_cheese_boiling_technology'}

    id = db.Column(db.Integer, db.ForeignKey('boiling_technologies.id'), primary_key=True)
    cooling_time = db.Column(db.Integer)
    heating_time = db.Column(db.Integer)
    adding_lactic_acid_time = db.Column(db.Integer)
    separation_time = db.Column(db.Integer)









