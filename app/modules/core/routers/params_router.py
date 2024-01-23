from typing import Optional
from fastapi import APIRouter, Depends
from app.common.response import StandardResponse, standard_response
from app.modules.core.services.country_service import CountryService, get_country_service
from app.modules.core.schemas.param_schemas import PublicParamsResponse

router = APIRouter()


@router.get(
    "/params/public/",
    response_model=StandardResponse[PublicParamsResponse],
    tags=["Params"]
)
async def get_public_parameters(
    include_countries: Optional[bool] = True,
    country_service: CountryService = Depends(get_country_service)
):
    result = PublicParamsResponse(countries=[])

    if include_countries:
        countries = await country_service.get_all()
        result.countries = [await country_service.get_country_response_from_country(country[0]) for country in countries]

    return standard_response(200, None, result)