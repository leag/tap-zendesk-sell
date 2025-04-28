"""Zendesk Sell deals stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterable

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream


class DealsStream(ZendeskSellStream):
    """Zendesk Sell deals stream class."""

    name = "deals"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "deals.json"

    @property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for deals."""
        base_schema = super().schema
        custom_fields_properties = self._update_schema({"deal"})
        if custom_fields_properties:
            if "properties" not in base_schema:
                base_schema["properties"] = {}
            base_schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a deal.",
                "type": ["object", "null"],
            }
        return base_schema

    def get_child_context(self, record: dict, _context: dict | None) -> dict:
        """Return a child context for the stream."""
        return {"deal_id": record["id"]}

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        while True:
            data = self.conn.deals.list(
                per_page=100,
                page=page,
                sort_by="id",
                includes="associated_contacts",
            )
            if not data:
                break
            yield from data
            page += 1


class AssociatedContacts(ZendeskSellStream):
    """Zendesk Sell associated contacts stream class."""

    name = "associated_contacts"
    parent_stream_type = DealsStream
    schema_filepath = SCHEMAS_DIR / "associated_contacts.json"

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        deal_id = context.get("deal_id") if context else None
        if deal_id is None:
            self.logger.warning(
                "Skipping AssociatedContacts: missing 'deal_id' in context."
            )
            return

        while True:
            data = self.conn.associated_contacts.list(
                deal_id=deal_id, page=page, per_page=100
            )
            if not data:
                break
            for row in data:
                row["deal_id"] = deal_id
                yield row
            page += 1
