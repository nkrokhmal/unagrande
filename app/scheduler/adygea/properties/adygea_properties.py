import pydantic

from pydantic import Field

from app.scheduler.time_utils import cast_human_time


class AdygeaProperties(pydantic.BaseModel):
    is_present: bool = Field(False, description="Присутствует ли моцарелла в этот день")

    end_time: str = Field("", description="Конец работы адыгейского цеха")
    n_boilings: str = Field(0, description="Количество варок")

    def department(self):
        return "adygea"
