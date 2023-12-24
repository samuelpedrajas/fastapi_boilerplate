from app.schemas import BaseModel
from typing import Optional
from datetime import datetime


class EmailTemplateResponse(BaseModel):
    id: Optional[int]
    name: str
    subject: str
    html_body: str
    created_at: datetime
    updated_at: datetime
