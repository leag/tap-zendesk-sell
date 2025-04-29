"""Zendesk Sell contacts stream class."""

from __future__ import annotations

from typing import ClassVar

import backoff
import requests

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream


class ContactsStream(ZendeskSellStream):
    """Zendesk Sell contacts stream class."""

    name = "contacts"
    primary_keys: ClassVar[list[str]] = ["id"]

    @property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties.

        This method is intentionally overridden to dynamically discover custom fields
        during catalog generation.
        """
        base_schema = super().schema
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

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.contacts.list(page=page, per_page=100)

    schema_filepath = SCHEMAS_DIR / "contacts.json"
