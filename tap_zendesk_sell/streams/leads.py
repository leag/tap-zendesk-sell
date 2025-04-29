"""Zendesk Sell leads stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import backoff
import requests

if TYPE_CHECKING:
    from collections.abc import Iterable

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

    name = "leads"
    primary_keys: ClassVar[list[str]] = ["id"]

    @property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for leads."""
        base_schema = super().schema
        custom_fields_properties = self._update_schema({"lead"})
        if custom_fields_properties:
            if "properties" not in base_schema:
                base_schema["properties"] = {}
            base_schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a lead.",
                "type": ["object", "null"],
            }
        return base_schema

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, per_page: int, page: int) -> list:
        """List data from the API."""
        return self.conn.leads.list(per_page=per_page, page=page, sort_by="id")

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        while True:
            data = self.list_data(per_page=100, page=page, sort_by="id")
            if not data:
                break
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "leads.json"
