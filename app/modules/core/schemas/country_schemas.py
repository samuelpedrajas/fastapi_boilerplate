from app.schemas import BaseModel


class CountryResponse(BaseModel):
    id: int
    code: str
    name: str
