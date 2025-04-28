"""Zendesk Sell lead sources stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR

if TYPE_CHECKING:
    from collections.abc import Iterable


class LeadSourcesStream(ZendeskSellStream):
    """Zendesk Sell lead sources stream class."""

    name = "lead_sources"
    primary_keys: ClassVar[list[str]] = ["id"]

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.lead_sources.list(per_page=100, page=page)
            if not data:
                finished = True
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "lead_sources.json"
