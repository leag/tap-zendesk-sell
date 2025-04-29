"""Zendesk Sell deals stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import backoff
import requests

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.helpers.types import Context


from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream


class DealsStream(ZendeskSellStream):
    """Zendesk Sell deals stream class."""

    name = "deals"
    primary_keys: ClassVar[list[str]] = ["id"]

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

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.deals.list(page=page, per_page=100)

    def get_child_context(
        self, record: dict, context: Context | None  # noqa: ARG002
    ) -> dict:
        """Return a child context for the stream."""
        return {"deal_id": record["id"]}

    schema_filepath = SCHEMAS_DIR / "deals.json"


class AssociatedContacts(ZendeskSellStream):
    """Zendesk Sell associated contacts stream class."""

    name = "associated_contacts"
    parent_stream_type = DealsStream
    schema_filepath = SCHEMAS_DIR / "associated_contacts.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, deal_id: int, page: int) -> list:
        """List associated contacts for a specific deal."""
        return self.conn.associated_contacts.list(
            deal_id, page=page, per_page=100
        )

    def get_records(self, context: Context | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        deal_id = context.get("deal_id") if context else None
        if deal_id is None:
            self.logger.warning(
                "Skipping AssociatedContacts: missing 'deal_id' in context."
            )
            return

        while True:
            data = self.list_data(deal_id=deal_id, page=page)
            if not data:
                break
            for row in data:
                row["deal_id"] = deal_id
                yield row
            page += 1
