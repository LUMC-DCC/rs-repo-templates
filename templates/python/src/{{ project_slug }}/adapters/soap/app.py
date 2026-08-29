"""WSGI SOAP application for {{ (project_name or project_slug) }}.

The application publishes SOAP 1.1 operations and generates a WSDL document
from the service declarations. An ASGI wrapper is exported for Uvicorn and for
composition with the project's other HTTP interfaces.
"""

from a2wsgi import WSGIMiddleware
from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from {{ project_slug }}.adapters.soap.service import ProcessingService


def create_wsgi_app() -> WsgiApplication:
    """Create the SOAP 1.1 WSGI application.

    Returns
    -------
    spyne.server.wsgi.WsgiApplication
        WSGI application that serves SOAP requests and ``?wsdl``.
    """
    soap = Application(
        [ProcessingService],
        tns="urn:{{ project_slug }}",
        in_protocol=Soap11(validator="lxml"),
        out_protocol=Soap11(),
    )
    return WsgiApplication(soap)


# Spyne is WSGI-native; this bridge lets the service run beside ASGI adapters.
wsgi_app = create_wsgi_app()
app = WSGIMiddleware(wsgi_app)

