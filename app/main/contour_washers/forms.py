from app.imports.runtime import *
from flask_wtf.file import FileRequired, FileField
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Required, Optional

from app.models import *


class ScheduleForm(FlaskForm):
    validators = [FileRequired(message="Отсутствует файл!")]
    date = DateTimeField("Введите дату", format="%Y-%m-%d", validators=[Required()])

    butter_end_time = TimeField(
        'Время окончания работы маслоцеха',
        validators=[Optional()],
        default=time(19, 0),
    )
    milkproject_end_time = TimeField(
        'Время окончания работы милкпроджекта',
        validators=[Optional()],
        default=time(11, 0),
    )
    adygea_end_time = TimeField(
        'Время окончания работы адыгейского цеха',
        validators=[Optional()],
        default=time(14, 0),
    )

    tank_4 = IntegerField(validators=[Optional()], default=0)
    tank_5 = IntegerField(validators=[Optional()], default=0)
    tank_8 = IntegerField(validators=[Optional()], default=0)
    is_not_working_day = BooleanField(
        "Завтра нерабочий день",
        validators=[Optional()],
        default=False,
    )