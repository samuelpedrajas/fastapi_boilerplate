from typing import List, Optional
from pydantic import BaseModel
from app.modules.core.schemas.country_schemas import CountryResponse

class PublicParamsResponse(BaseModel):
    countries: Optional[List[CountryResponse]]
