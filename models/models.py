from pydantic import BaseModel, ConfigDict, Field

def DutchBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
    )

def Sense(DutchBaseModel):
    pass