"""Zendesk Sell visits stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable


class VisitsStream(ZendeskSellStream):
    """Zendesk Sell visits stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/visits/
    """

    name = "visits"
    primary_keys = ("id",)

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        while True:
            data = self.list_data(
                self.conn.visits.list, per_page=100, page=page, sort_by="id"
            )
            if not data:
                break
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "visits.json"
