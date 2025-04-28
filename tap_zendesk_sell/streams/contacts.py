"""Zendesk Sell contacts stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterable


from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class ContactsStream(ZendeskSellStream):
    """Zendesk Sell contacts stream class."""

    name = "contacts"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "contacts.json"

    @property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties.

        This method is intentionally overridden to dynamically discover custom fields
        during catalog generation.
        """
        base_schema = super().schema
        # self.conn is now guaranteed to be initialized by the base property
        custom_fields_properties = self._update_schema({"contact"})
        if custom_fields_properties:
            if "properties" not in base_schema:
                base_schema["properties"] = {}
            base_schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a contact.",
                "type": ["object", "null"],
            }
        return base_schema

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.contacts.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
                continue
            yield from data
            page += 1
