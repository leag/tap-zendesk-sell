"""Zendesk Sell leads stream class."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/leads/
    """

    name = "leads"
    primary_keys = ("id",)

    @cached_property
    def schema(self) -> dict:
        """Return the schema for the stream."""
        base_schema = super().schema
        custom_fields_properties = self._build_custom_field_schema(
            {
                "lead",
            }
        )
        if custom_fields_properties:
            base_schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a lead.",
                "type": ["object", "null"],
            }
        return base_schema

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.list_data(
                self.conn.leads.list, per_page=100, page=page, sort_by="id"
            )
            if not data:
                finished = True
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "leads.json"
