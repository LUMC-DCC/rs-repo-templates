"""Repository boundary for portal records.

Repositories hide where portal data comes from. This starter repository uses
in-memory records, but the rest of the portal can keep the same interface if the
data later moves to a file, database, or external API.
"""

from collections.abc import Sequence

from {{ project_slug }}.adapters.portal.models import PortalRecord


class PortalRepository:
    """In-memory repository for portal records."""

    def __init__(self, records: Sequence[PortalRecord] | None = None):
        """Create a portal repository.

        Parameters
        ----------
        records : collections.abc.Sequence[PortalRecord] | None, optional
            Records to expose through the portal.
        """
        # Copy records into a list so callers cannot mutate repository state by
        # changing the original sequence after construction.
        self._records = list(records or default_records())

    def list_records(self) -> list[PortalRecord]:
        """Return portal records.

        Returns
        -------
        list[PortalRecord]
            Records available to the portal.
        """
        return list(self._records)


def default_records() -> list[PortalRecord]:
    """Return starter portal records.

    Returns
    -------
    list[PortalRecord]
        Starter portal records.
    """
    # The generated record gives the portal something useful to render before a
    # real data source is connected.
    return [
        PortalRecord(
            identifier="example",
            label="{{ (project_name or project_slug) }}",
            description="{{ project_short_description }}",
        )
    ]
