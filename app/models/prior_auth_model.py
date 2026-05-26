from datetime import datetime, time
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field, ValidationInfo, create_model, field_validator


class PriorAuthBaseModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def convert_temporal_types(cls, v: Any, info: ValidationInfo) -> Any:
        """
        Convert string back to datetime or time if the target field type is temporal
        but the provided value is a string.
        """
        if not isinstance(v, str):
            return v

        field_info = cls.model_fields.get(info.field_name)
        if not field_info:
            return v

        annotation = field_info.annotation

        # Check if the annotation is datetime or time (including Optional/Union variants)
        is_datetime_type = False
        is_time_type = False

        if annotation is datetime:
            is_datetime_type = True
        elif annotation is time:
            is_time_type = True
        else:
            # Handle Optional / Union / | types
            origin = getattr(annotation, "__origin__", None)
            args = getattr(annotation, "__args__", ())
            if origin is Union:
                if datetime in args:
                    is_datetime_type = True
                if time in args:
                    is_time_type = True
            else:
                # Fallback for Python 3.10+ | syntax or other variant representations
                anno_str = str(annotation)
                if "datetime.datetime" in anno_str or "datetime" in anno_str:
                    is_datetime_type = True
                elif "datetime.time" in anno_str or "time" in anno_str:
                    is_time_type = True

        if is_datetime_type:
            try:
                # Handle ISO format strings, including 'Z' suffix
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return v

        if is_time_type:
            try:
                # Handle ISO format time strings (e.g., "14:30:00")
                return time.fromisoformat(v)
            except (ValueError, TypeError):
                return v

        return v


def get_prior_auth_output_model(fields: List[Dict[str, Any]]) -> Type[BaseModel]:
    """
    Dynamically creates a Pydantic model for LLM output based on field definitions.

    Args:
        fields: A list of dictionaries containing 'name', 'type', and 'description'.

    Returns:
        A dynamically generated Pydantic model class.
    """
    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "datetime": datetime,
        "time": time,
        "None": type(None),
    }

    dyn_fields = {}
    for f in fields:
        f_name = f.get("name")
        if not f_name:
            continue

        f_type_str = f.get("type", "str")
        f_type = type_mapping.get(f_type_str, str)
        f_desc = f.get("description", "")

        # Using Optional[f_type] with default None ensures the model can handle missing values
        dyn_fields[f_name] = (Optional[f_type], Field(default=None, description=f_desc))

    # Create the dynamic model using PriorAuthBaseModel as the base class
    return create_model(
        "PriorAuthOutputModel",
        __base__=PriorAuthBaseModel,
        **dyn_fields
    )