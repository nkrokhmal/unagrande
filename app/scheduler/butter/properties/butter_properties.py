import pydantic

from pydantic import Field

from app.scheduler.time_utils import cast_human_time


class ButterProperties(pydantic.BaseModel):
    is_present: bool = Field(False, description="Присутствует ли масло в этот день")

    end_time: str = Field("", description="Конец работы маслоцеха")

    def department(self):
        return "butter"
