"""Zendesk Sell contacts stream class."""
from typing import Iterable, Optional

from singer_sdk.tap_base import Tap

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class ContactsStream(ZendeskSellStream):
    """Zendesk Sell contacts stream class."""

    name = "contacts"
    primary_keys = ["id"]

    def __init__(self, tap: Tap):
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
            }

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.contacts.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
            for row in data:
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "contacts.json"
