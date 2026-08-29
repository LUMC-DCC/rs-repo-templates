"""Read structured values from the normalized Copier context."""


def entries(ctx, field_name):
    """Return entries from one structured repeatable context field.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Public contract field containing an ``entries`` list.

    Returns
    -------
    list
        Rendered entries, or an empty list for a missing or invalid field.
    """
    field = ctx.get(field_name, {})
    if not isinstance(field, dict):
        return []
    values = field.get("entries", [])
    return values if isinstance(values, list) else []


def object_value(ctx, field_name, property_name, default=""):
    """Return one value from a structured context field.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Public object field name.
    property_name : str
        Property to read from the object.
    default : object, optional
        Value returned when the field or property is absent.

    Returns
    -------
    object
        Stored property value, or ``default`` for an invalid object.
    """
    field = ctx.get(field_name, {})
    if not isinstance(field, dict):
        return default
    return field.get(property_name, default)


def object_entries(ctx, field_name, property_name):
    """Return entries from a repeatable property inside an object field.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Public object field name.
    property_name : str
        Property containing an ``entries`` wrapper.

    Returns
    -------
    list
        Rendered entries, or an empty list for a missing or invalid property.
    """
    value = object_value(ctx, field_name, property_name, {})
    if not isinstance(value, dict):
        return []
    values = value.get("entries", [])
    return values if isinstance(values, list) else []


def normalize_choice(value):
    """Normalize one selector value for comparison.

    Parameters
    ----------
    value : object
        Raw selector value.

    Returns
    -------
    str
        Lowercase selector value without surrounding whitespace.
    """
    return str(value or "").strip().lower()


def template_default(ctx, field_name):
    """Return one template-specific default value.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Public contract field name.

    Returns
    -------
    object
        Configured template default, or ``None`` when absent.
    """
    defaults = ctx.get("_template_defaults", {})
    if not isinstance(defaults, dict):
        return None
    return defaults.get(field_name)


def template_supported_choices(ctx, field_name):
    """Return normalized choices supported by one template.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Public contract field name.

    Returns
    -------
    list[str]
        Supported choices in configured order.
    """
    supported = ctx.get("_template_supported_choices", {})
    if not isinstance(supported, dict):
        return []
    choices = supported.get(field_name, [])
    if not isinstance(choices, list):
        return []
    return [
        normalized for choice in choices if (normalized := normalize_choice(choice))
    ]


def template_supported_object_choices(ctx, field_name, property_name):
    """Return normalized choices for one property of an object selector.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Public object field name.
    property_name : str
        Selector property within the object.

    Returns
    -------
    list[str]
        Choices supported by the selected template.
    """
    supported = ctx.get("_template_supported_choices", {})
    if not isinstance(supported, dict):
        return []
    field_choices = supported.get(field_name, {})
    if not isinstance(field_choices, dict):
        return []
    choices = field_choices.get(property_name, [])
    if not isinstance(choices, list):
        return []
    return [
        normalized for choice in choices if (normalized := normalize_choice(choice))
    ]


def resolve_choice(ctx, field_name, fallback=""):
    """Resolve one selector against template-specific capabilities.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Public selector field name.
    fallback : str, default=""
        Value used when neither the request nor template default is supported.

    Returns
    -------
    tuple[str, str]
        Requested and effective normalized selector values.
    """
    requested = normalize_choice(ctx.get(field_name))
    default = normalize_choice(template_default(ctx, field_name))
    supported = set(template_supported_choices(ctx, field_name))

    if requested in supported:
        return requested, requested
    if default in supported:
        return requested, default
    return requested, normalize_choice(fallback)


def resolve_object_choice(ctx, field_name, property_name, fallback=""):
    """Resolve one object property against template capabilities.

    Parameters
    ----------
    ctx : dict
        Normalized Copier context.
    field_name : str
        Public object field name.
    property_name : str
        Selector property within the object.
    fallback : str, default=""
        Value used when the request is unsupported.

    Returns
    -------
    tuple[str, str]
        Requested and effective normalized selector values.
    """
    requested = normalize_choice(object_value(ctx, field_name, property_name))
    supported = set(template_supported_object_choices(ctx, field_name, property_name))
    if requested in supported:
        return requested, requested
    return requested, normalize_choice(fallback)
