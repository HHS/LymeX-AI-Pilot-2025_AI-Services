from pydantic import BaseModel, Field
from typing import Any, get_origin, get_args, Union


# IGNORE THAT, PREFER EXPLICIT DEFAULTS
class SafeBase(BaseModel):
    """
    A drop-in replacement for BaseModel that

    • turns every Optional[...] field with no explicit default into =None
    • turns every List[...] field with no explicit default into =[]
    • leaves required scalars (str, int, bool, etc.) untouched
    """

    def __init_subclass__(cls, **kwargs):  # runs once per subclass definition
        super().__init_subclass__(**kwargs)

        for name, field in cls.__fields__.items():
            outer_type = field.outer_type_
            origin = get_origin(outer_type)

            # ── Optional[…] with no default ➜ default None
            if origin is type(None) or (
                origin is Union and type(None) in get_args(outer_type)
            ):
                if field.default is Ellipsis:  # i.e. “required”
                    field.default = None
                    field.required = False

            # ── List[…]/set[…]/dict[…], no default ➜ default_factory=list/set/dict
            elif origin in (list, set, dict):
                if field.default is Ellipsis:
                    factory = list if origin is list else set if origin is set else dict
                    field.default_factory = factory
                    field.required = False

    class Config:
        # silently ignore unknown keys the LLM might slip in
        extra = "ignore"
