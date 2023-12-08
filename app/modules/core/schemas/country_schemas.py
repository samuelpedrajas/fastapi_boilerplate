from pydantic import BaseModel


class CountryResponse(BaseModel):
    country_id: int
    code: str
    name: str
