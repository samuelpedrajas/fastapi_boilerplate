from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, Relationship
from app.common.base_model import BaseModel

class EmailTemplateEmailVariable(BaseModel, table=True):
    __tablename__ = "email_templates_email_variables"

    id: Optional[int] = Field(default=None, primary_key=True)
    email_template_id: int = Field(foreign_key="email_templates.id")
    email_variable_id: int = Field(foreign_key="email_variables.id")


class EmailVariable(BaseModel, table=True):
    __tablename__ = 'email_variables'

    id: Optional[int] = Field(default=None, primary_key=True)
    variable: str
    description: Optional[str] = None

    email_templates: List["EmailTemplate"] = Relationship(back_populates="email_variables", link_model=EmailTemplateEmailVariable)


class EmailTemplate(BaseModel, table=True):
    __tablename__ = 'email_templates'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    subject: str
    html_body: str

    email_variables: List[EmailVariable] = Relationship(back_populates="email_templates",
                                                        link_model=EmailTemplateEmailVariable,
                                                        sa_relationship_kwargs={'lazy': 'joined'})
