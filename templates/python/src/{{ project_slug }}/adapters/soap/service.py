"""SOAP service operations for {{ (project_name or project_slug) }}.

Spyne declarations define the wire contract and generated WSDL. Operations
delegate reusable work to the service layer so transport code stays small.
"""

from spyne import ServiceBase, Unicode, rpc

from {{ project_slug }}.services.processing import process_text


class ProcessingService(ServiceBase):
    """Expose project processing through a SOAP 1.1 operation."""

    @rpc(Unicode, _returns=Unicode)
    def process(ctx, text: str) -> str:
        """Process text and return the transformed value.

        Parameters
        ----------
        ctx : spyne.MethodContext
            Request context supplied by Spyne.
        text : str
            Input text from the SOAP request.

        Returns
        -------
        str
            Processed text.
        """
        # Keep SOAP serialization here and reusable behavior in the service.
        del ctx
        return process_text(text).output_text

