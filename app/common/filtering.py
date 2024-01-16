from typing import Any, Callable, Dict, List, Tuple
from fastapi import Query
from pydantic import BaseModel as BaseSchema
from sqlalchemy import AliasedReturnsRows, Select, and_, func
from sqlalchemy.orm import aliased
from app.common.base_model import BaseModel


class FilterConfig:
    def __init__(self, 
                 model_fields: List[str], 
                 comparison: Callable[[Any, Any, List[Any]], Any]):
        self.model_fields = model_fields
        self.comparison = comparison


class BaseFiltering(BaseSchema):
    def apply_filters(self) -> Query:
        model, filters_config = self.filters_config()
        query = Select(model)
        conditions = []

        for field_name, filter_config in filters_config.items():
            value = getattr(self, field_name, None)
            if value is not None:
                if len(filter_config.model_fields) > 1:
                    # Handle multiple fields (e.g., concatenating fields)
                    fields = []
                    for model_field in filter_config.model_fields:
                        field = self.resolve_field(model, model_field)
                        fields.append(field)
                    condition = filter_config.comparison(fields, value)
                    conditions.append(condition)
                else:
                    # Handle single field
                    for model_field in filter_config.model_fields:
                        parts = model_field.split('.')
                        current_model = model
                        for i, part in enumerate(parts[:-1]):
                            relationship_attr = getattr(current_model, part)
                            if hasattr(relationship_attr, 'property') and hasattr(relationship_attr.property, 'mapper'):
                                related_model = aliased(relationship_attr.property.mapper.class_)
                                # Explicit ON clause for join
                                query = query.join(related_model, relationship_attr)
                                current_model = related_model
                            else:
                                raise AttributeError(f"Relationship '{part}' not found in {current_model.__name__}")

                        final_field = getattr(current_model, parts[-1], None)
                        condition = filter_config.comparison([final_field], value)
                        conditions.append(condition)

        if conditions:
            query = query.where(and_(*conditions))

        return query

    def resolve_field(self, model, field_path: str):
        field_parts = field_path.split('.')
        current_model = model

        for part in field_parts:
            if hasattr(current_model, part):
                field = getattr(current_model, part)
                if hasattr(field, 'property') and hasattr(field.property, 'mapper'):
                    # It's a relationship; switch to related model
                    current_model = field.property.mapper.class_
                else:
                    # It's a direct field
                    current_model = field
            else:
                raise AttributeError(f"Field or relationship '{part}' not found in {current_model.__name__}")

        return current_model

    def filters_config(self) -> Tuple[BaseModel, Dict[str, FilterConfig]]:
        raise NotImplementedError  # Override in subclass


# Comparison functions

def equals(fields, input_value):
    if len(fields) > 1:
        raise ValueError("Equals comparison function expects only one field.")
    return fields[0] == input_value


def greater_than(fields, input_value):
    if len(fields) > 1:
        raise ValueError("Greater than comparison function expects only one field.")
    return fields[0] > input_value


def less_than(fields, input_value):
    if len(fields) > 1:
        raise ValueError("Less than comparison function expects only one field.")
    return fields[0] < input_value


def greater_than_or_equal(fields, input_value):
    if len(fields) > 1:
        raise ValueError("Greater than or equal to comparison function expects only one field.")
    return fields[0] >= input_value


def less_than_or_equal(fields, input_value):
    if len(fields) > 1:
        raise ValueError("Less than or equal to comparison function expects only one field.")
    return fields[0] <= input_value


def enhanced_ilike(fields, input_value):
    '''This function concatenates all fields, like "name" and "surname" with a space in between,
    then it applies both unaccent and lower functions and finally applies an ilike comparison.'''
    concatenated_fields = func.lower(func.unaccent(func.concat_ws(' ', *fields)))
    cleaned_input = func.lower(func.unaccent(f'%{input_value}%'))
    return concatenated_fields.ilike(cleaned_input)
