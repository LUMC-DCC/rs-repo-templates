"""Typed runtime configuration for {{ (cookiecutter.project_name or cookiecutter.project_slug) }}.

Settings are read from environment variables prefixed with
``{{ cookiecutter.project_slug | upper }}_``. A local ``.env`` file is supported
for development and is excluded from version control. Production deployments
should inject values through their platform or secrets manager.
"""

from functools import lru_cache
from typing import Literal

{% set interface_types = namespace(values=[]) %}
{% for interface in cookiecutter.interfaces.entries %}
{% if interface.type is defined and interface.type %}
{% set _ = interface_types.values.append(interface.type) %}
{% endif %}
{% endfor %}
{% set has_http_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Web service" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% set has_openapi_interface = "Web API" in interface_types.values or "SPARQL endpoint" in interface_types.values or "Bioinformatics portal" in interface_types.values or "Database portal" in interface_types.values or "Web application" in interface_types.values or "Workbench" in interface_types.values %}
{% if has_openapi_interface %}
from pydantic import AnyHttpUrl, Field, field_validator
{% elif has_http_interface %}
from pydantic import Field, field_validator
{% endif %}
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings shared by generated runtime adapters.

    Parameters
    ----------
    log_level : {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        Application logging threshold.
{% if has_http_interface %}
    server_host : str
        Network interface on which the HTTP server listens.
    server_port : int
        TCP port on which the HTTP server listens.
    server_root_path : str
        Optional URL path used when the application is mounted by a proxy.
    server_reload : bool
        Whether the development server watches source files for changes.
{% if has_openapi_interface %}
    public_base_url : pydantic.AnyHttpUrl | None
        Optional externally visible URL published in API metadata.
{% endif %}
{% endif %}
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="{{ cookiecutter.project_slug | upper }}_",
        extra="ignore",
    )

    log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
{% if has_http_interface %}
    server_host: str = Field(default="127.0.0.1", min_length=1)
    server_port: int = Field(default=8000, ge=1, le=65535)
    server_root_path: str = ""
    server_reload: bool = False
{% if has_openapi_interface %}
    public_base_url: AnyHttpUrl | None = None
{% endif %}

    @field_validator("server_host")
    @classmethod
    def normalize_server_host(cls, value: str) -> str:
        """Strip surrounding whitespace from a non-empty bind host.

        Parameters
        ----------
        value : str
            Configured bind host.

        Returns
        -------
        str
            Normalized bind host.

        Raises
        ------
        ValueError
            If the host contains only whitespace.
        """
        normalized = value.strip()
        if not normalized:
            raise ValueError("Server host must not be empty")
        return normalized

    @field_validator("server_root_path")
    @classmethod
    def normalize_server_root_path(cls, value: str) -> str:
        """Normalize a non-empty proxy root path.

        Parameters
        ----------
        value : str
            Configured root path.

        Returns
        -------
        str
            Empty string or one slash-prefixed path without a trailing slash.
        """
        normalized = value.strip().strip("/")
        return f"/{normalized}" if normalized else ""
{% endif %}


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings object for the current process.

    Returns
    -------
    Settings
        Validated runtime settings.
    """
    return Settings()
