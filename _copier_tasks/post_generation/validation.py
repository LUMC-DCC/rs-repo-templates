"""Validate template-specific context constraints before finalization."""

import re

from rsm_schema import RSMMetadata, validate_document
from utils.rsm import rsm_payload


def validate_string(value, schema, field_name, template_name):
    """Validate one string against the supported contract fragment.

    Parameters
    ----------
    value : object
        Rendered context value.
    schema : dict
        Template-specific JSON Schema fragment.
    field_name : str
        Public context field name.
    template_name : str
        Selected template language.

    Raises
    ------
    ValueError
        If the value violates a configured constraint.
    """
    valid = isinstance(value, str)
    valid = valid and len(value) >= schema.get("minLength", 0)
    valid = valid and len(value) <= schema.get("maxLength", len(value))

    pattern = schema.get("pattern")
    if pattern:
        valid = valid and re.search(pattern, value) is not None

    allowed_values = schema.get("enum")
    if allowed_values is not None:
        valid = valid and value in allowed_values

    forbidden_values = schema.get("not", {}).get("enum", [])
    valid = valid and value not in forbidden_values

    if not valid:
        guidance = schema.get(
            "description", "The value does not satisfy the template constraints."
        )
        raise ValueError(
            f"Invalid {field_name!r} value {value!r} for the {template_name} "
            f"template. {guidance}"
        )


def validate_context(ctx):
    """Validate RSM metadata and template-specific context fields.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.

    Raises
    ------
    ValueError
        If any field violates its selected template constraint.
    """
    public_context = rsm_payload(ctx, RSMMetadata.model_fields)
    validate_document(public_context)
    RSMMetadata.model_validate(public_context)

    schemas = ctx.get("_template_schemas", {})
    if not isinstance(schemas, dict):
        return

    template_name = str(ctx.get("_template_name", "selected"))
    for field_name, schema in schemas.items():
        if isinstance(schema, dict):
            validate_string(ctx.get(field_name), schema, field_name, template_name)
