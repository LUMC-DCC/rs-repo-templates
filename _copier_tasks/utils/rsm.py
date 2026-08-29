"""Adapt rendered Copier values to the published RSM data shape."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def omit_empty_properties(value):
    """Remove empty-string object properties recursively.

    Copier finalization uses an empty string for an unselected scalar prompt. The RSM
    schema expresses the same state by omitting the optional property.

    Parameters
    ----------
    value : Any
        Rendered context value.

    Returns
    -------
    Any
        Value with empty object properties omitted and list entries preserved.
    """
    if isinstance(value, Mapping):
        return {
            key: omit_empty_properties(item)
            for key, item in value.items()
            if item != ""
        }
    if isinstance(value, list):
        return [omit_empty_properties(item) for item in value]
    return value


def rsm_payload(ctx, field_names: Iterable[str]):
    """Select and normalize public RSM fields from a rendered context.

    Parameters
    ----------
    ctx : Mapping[str, Any]
        Normalized Copier context.
    field_names : Iterable[str]
        Public fields accepted by the target RSM model.

    Returns
    -------
    dict[str, Any]
        Normalized RSM payload.
    """
    selected = {
        field_name: ctx[field_name] for field_name in field_names if field_name in ctx
    }
    return omit_empty_properties(selected)
