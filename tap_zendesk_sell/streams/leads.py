"""Zendesk Sell leads stream class."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from tenacity import retry, stop_after_attempt, wait_exponential

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def list_data(self, per_page: int, page: int) -> list:
        """List data from the API."""
        return self.conn.leads.list(per_page=per_page, page=page, sort_by="id")

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.list_data(per_page=100, page=page)
            if not data:
                finished = True
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "leads.json"
