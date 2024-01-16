from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.common.base_model import BaseModel


class EmailTemplateEmailVariable(BaseModel):
    __tablename__ = "email_templates_email_variables"

    email_template_id = Column(Integer, ForeignKey('email_templates.id'), primary_key=True)
    email_variable_id = Column(Integer, ForeignKey('email_variables.id'), primary_key=True)



class EmailVariable(BaseModel):
    __tablename__ = 'email_variables'

    variable = Column(String)
    description = Column(String, nullable=True)

    email_templates = relationship("EmailTemplate", 
                                   secondary="email_templates_email_variables",
                                   back_populates="email_variables")

class EmailTemplate(BaseModel):
    __tablename__ = 'email_templates'

    name = Column(String)
    subject = Column(String)
    html_body = Column(String)

    email_variables = relationship("EmailVariable", 
                                   secondary="email_templates_email_variables",
                                   back_populates="email_templates",
                                   lazy='joined')
