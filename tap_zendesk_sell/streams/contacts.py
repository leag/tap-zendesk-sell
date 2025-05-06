"""Zendesk Sell contacts stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.tap_base import Tap


class ContactsStream(ZendeskSellStream):
    """Zendesk Sell contacts stream class."""

    name = "contacts"
    primary_keys = ("id",)

    def __init__(self, tap: Tap) -> None:
        """Initialize the stream."""
        super().__init__(tap)
        """Initialize the stream."""
        custom_fields_properties = self._update_schema(
            {
                "contact",
            }
        )
        if custom_fields_properties:
            self._schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a contact.",
                "type": ["object", "null"],
            }

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.contacts.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "contacts.json"
