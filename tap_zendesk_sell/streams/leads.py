"""Zendesk Sell leads stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

# Sort imports and add necessary ones
import backoff
import requests

if TYPE_CHECKING:
    from collections.abc import Iterable

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

    name = "leads"
    # Annotate primary_keys
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "leads.json"

    @property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for leads."""
        base_schema = super().schema
        # self.conn is now guaranteed to be initialized by the base property
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
        # Connection is guaranteed to be initialized by now
        return self.conn.leads.list(per_page=per_page, page=page, sort_by="id")

    # Use | for Optional type hint, mark context unused
    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.list_data(per_page=100, page=page)
            if not data:
                finished = True
                continue
            yield from data
            page += 1
