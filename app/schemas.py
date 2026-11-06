from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

class UserCreate(BaseModel):
    student_id: Annotated[str,StringConstraints(
        pattern=r"^ST\^BT\d{4}$")]

    equipment_id: int = Field(gt=1, lt=999999999999999999)
    priority: int = Field(gt=1, lt=5)
    descripton: Annotated[str,StringConstraints
    (min_length=5, max_length=100)]  
 