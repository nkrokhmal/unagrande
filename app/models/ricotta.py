from sqlalchemy.orm import backref

from app.globals import mdb
from app.models.basic import SKU, Boiling, BoilingTechnology, FormFactor, Line


class RicottaSKU(SKU):
    __tablename__ = "ricotta_skus"
    __mapper_args__ = {"polymorphic_identity": "ricotta_skus"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True)
    output_per_tank = mdb.Column(mdb.Float)
    at_first = mdb.Column(mdb.Boolean)


class RicottaLine(Line):
    __tablename__ = "ricotta_lines"
    __mapper_args__ = {"polymorphic_identity": "ricotta_lines"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), primary_key=True)
    input_ton = mdb.Column(mdb.Integer)


class RicottaFormFactor(FormFactor):
    __tablename__ = "ricotta_form_factors"
    __mapper_args__ = {"polymorphic_identity": "ricotta_form_factor"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("form_factors.id"), primary_key=True)


class RicottaBoiling(Boiling):
    __tablename__ = "ricotta_boilings"
    __mapper_args__ = {"polymorphic_identity": "ricotta_boiling"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True)
    flavoring_agent = mdb.Column(mdb.String)
    percent = mdb.Column(mdb.Integer)
    number_of_tanks = mdb.Column(mdb.Integer)

    analysis = mdb.relationship(
        "RicottaAnalysisTechnology",
        backref=backref("boiling", uselist=False, lazy="subquery"),
    )

    @property
    def with_flavor(self) -> bool:
        return self.flavoring_agent != ""

    @property
    def short_display_name(self) -> str:
        return self.flavoring_agent if self.flavoring_agent else "Рикотта"

    @property
    def is_cream(self) -> bool:
        return self.percent == 30 and not self.with_flavor

    def to_str(self) -> str:
        return f"{self.percent}, {self.flavoring_agent}"


class RicottaBoilingTechnology(BoilingTechnology):
    __tablename__ = "ricotta_boiling_technologies"
    __mapper_args__ = {"polymorphic_identity": "ricotta_boiling_technology"}

    id = mdb.Column(mdb.Integer, mdb.ForeignKey("boiling_technologies.id"), primary_key=True)
    heating_time = mdb.Column(mdb.Integer)
    delay_time = mdb.Column(mdb.Integer)
    protein_harvest_time = mdb.Column(mdb.Integer)
    abandon_time = mdb.Column(mdb.Integer)
    pumping_out_time = mdb.Column(mdb.Integer)

    @staticmethod
    def create_name(line: str, percent: float | int, flavoring_agent: str) -> str:
        return f"Линия {line}, {percent}, {flavoring_agent}"


class RicottaAnalysisTechnology(mdb.Model):
    __tablename__ = "ricotta_analyses_technology"
    id = mdb.Column(mdb.Integer, primary_key=True)
    preparation_time = mdb.Column(mdb.Integer)
    analysis_time = mdb.Column(mdb.Integer)
    pumping_time = mdb.Column(mdb.Integer)

    boiling_id = mdb.Column(mdb.Integer, mdb.ForeignKey("ricotta_boilings.id"), nullable=True)


__all__ = [
    "RicottaBoilingTechnology",
    "RicottaBoiling",
    "RicottaAnalysisTechnology",
    "RicottaLine",
    "RicottaSKU",
    "RicottaFormFactor",
]
