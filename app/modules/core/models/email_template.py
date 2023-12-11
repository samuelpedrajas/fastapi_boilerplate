from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class EmailTemplateEmailVariable(SQLModel, table=True):
    __tablename__ = "email_templates_email_variables"

    id: Optional[int] = Field(default=None, primary_key=True)
    email_template_id: int = Field(foreign_key="email_templates.id")
    email_variable_id: int = Field(foreign_key="email_variables.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})


class EmailVariable(SQLModel, table=True):
    __tablename__ = 'email_variables'

    id: Optional[int] = Field(default=None, primary_key=True)
    variable: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    email_templates: List["EmailTemplate"] = Relationship(back_populates="email_variables", link_model=EmailTemplateEmailVariable)


class EmailTemplate(SQLModel, table=True):
    __tablename__ = 'email_templates'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    subject: str
    html_body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})

    email_variables: List[EmailVariable] = Relationship(back_populates="email_templates", link_model=EmailTemplateEmailVariable)
