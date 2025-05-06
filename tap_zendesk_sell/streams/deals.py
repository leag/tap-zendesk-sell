"""Zendesk Sell deals stream class."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable



class DealsStream(ZendeskSellStream):
    """Zendesk Sell deals stream class."""

    name = "deals"
    primary_keys = ("id",)

    @cached_property
    def schema(self) -> dict:
        """Return the schema for the stream."""
        base_schema = super().schema
        custom_fields_properties = self._build_custom_field_schema(
            {
                "deal",
            }
        )
        if custom_fields_properties:
            base_schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a deal.",
                "type": ["object", "null"],
            }
        return base_schema

    def get_child_context(self, record: dict, context: dict | None) -> dict:  # noqa: ARG002
        """Return a child context for the stream."""
        return {"deal_id": record["id"]}

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.deals.list(
                per_page=100, page=page, sort_by="id", includes="associated_contacts"
            )
            if not data:
                finished = True
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "deals.json"


class AssociatedContacts(ZendeskSellStream):
    """Zendesk Sell asociated contacts stream class."""

    name = "associated_contacts"
    parent_stream_type = DealsStream

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.associated_contacts.list(
                deal_id=context.get("deal_id"), page=page, per_page=100
            )
            if not data:
                finished = True
            for row in data:
                row["deal_id"] = context.get("deal_id")
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "associated_contacts.json"
