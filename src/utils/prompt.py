from datetime import datetime
from typing import Dict, List, Union, get_args, get_origin
from enum import Enum

from pydantic import BaseModel, Field
from pydantic_core import PydanticUndefined


def get_enum_values(enum_type):
    return [e.value for e in enum_type]


def field_type_repr(field_type):
    origin = get_origin(field_type)
    if origin is Union:
        args = get_args(field_type)
        if type(None) in args:
            other = [a for a in args if a is not type(None)]
            return f"{field_type_repr(other[0])} | null"
        else:
            return " | ".join([field_type_repr(a) for a in args])
    if origin is list or origin is List:
        item_type = get_args(field_type)[0]
        return f"list[{field_type_repr(item_type)}]"
    if origin is dict or origin is Dict:
        key_type, val_type = get_args(field_type)
        return f"dict[{field_type_repr(key_type)}, {field_type_repr(val_type)}]"
    if hasattr(field_type, "__fields__"):
        return "object"
    if isinstance(field_type, type) and issubclass(field_type, Enum):
        return (
            "enum(" + " | ".join([repr(v) for v in get_enum_values(field_type)]) + ")"
        )
    if field_type is str:
        return "string"
    if field_type is int:
        return "int"
    if field_type is bool:
        return "boolean"
    if field_type is float:
        return "float"
    if field_type is datetime:
        return "ISO8601 datetime string"
    return str(field_type)


def get_field_default(field):
    # Return a printable version of the default value, skip if Ellipsis (required)
    default = field.default
    if default is ...:
        return None
    if isinstance(default, Enum):
        return default.value
    return repr(default)


def get_field_description(field):
    # Works for Pydantic v2, fallback for v1 (field.field_info.description)
    if hasattr(field, "description") and field.description:
        return field.description
    if hasattr(field, "field_info") and hasattr(field.field_info, "description"):
        return field.field_info.description
    return None


def model_to_schema(model: type[BaseModel], indent: int = 0) -> str:
    pad = "  " * indent
    lines = ["{"]
    for name, field in model.model_fields.items():
        typ = field.annotation
        if hasattr(typ, "__fields__"):  # Nested model
            value = model_to_schema(typ, indent + 1)
        elif get_origin(typ) in [list, List]:
            subtyp = get_args(typ)[0]
            if hasattr(subtyp, "__fields__"):
                value = f"[{model_to_schema(subtyp, indent + 2)}{pad}  ]"
            elif isinstance(subtyp, type) and issubclass(subtyp, Enum):
                value = f"list[{field_type_repr(subtyp)}]"
            else:
                value = f"list[{field_type_repr(subtyp)}]"
        elif isinstance(typ, type) and issubclass(typ, Enum):
            value = field_type_repr(typ)
        else:
            value = field_type_repr(typ)

        # Get default and description
        default = get_field_default(field)
        desc = get_field_description(field)
        meta = []
        if default is not None and default is not PydanticUndefined:
            meta.append(f"default={default}")
        if desc:
            meta.append(f"description={desc!r}")
        meta_str = f"  // {', '.join(meta)}" if meta else ""
        lines.append(f'{pad}  "{name}": {value},{meta_str}')
    lines.append(pad + "}")
    return "\n".join(lines)


if __name__ == "__main__":

    class Status(Enum):
        active = "active"
        inactive = "inactive"

    class ExampleModel(BaseModel):
        name: str = Field("John Doe", description="The name of the person")
        age: int = Field(30, description="The age of the person")
        is_active: bool = Field(True, description="Whether the person is active")
        tags: List[str] = Field(["tag1", "tag2"], description="List of tags")
        metadata: Dict[str, Union[str, int]] = Field(
            {"key1": "value1", "key2": 2}, description="Metadata dictionary"
        )
        status: Status = Field(Status.active, description="Status of the person")

    print(model_to_schema(ExampleModel))
