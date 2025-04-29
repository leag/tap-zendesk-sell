"""Zendesk Sell leads stream class."""

from __future__ import annotations

from typing import ClassVar

import backoff
import requests

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
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.leads.list(page=page, per_page=100)

    schema_filepath = SCHEMAS_DIR / "leads.json"
