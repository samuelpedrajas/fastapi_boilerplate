from typing import List, Optional
from pydantic import BaseModel
from app.modules.core.schemas.country_schemas import CountryResponse
from app.modules.core.schemas.user_schemas import RoleResponse

class PublicParamsResponse(BaseModel):
    countries: Optional[List[CountryResponse]]
    roles: Optional[List[RoleResponse]]
