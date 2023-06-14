"""Zendesk Sell deals stream class."""
from typing import Iterable, Optional

from singer_sdk.tap_base import Tap

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class DealsStream(ZendeskSellStream):
    """Zendesk Sell deals stream class."""

    name = "deals"
    primary_keys = ["id"]

    def __init__(self, tap: Tap):
        """Initialize the stream."""
        super().__init__(tap)
        custom_fields_properties = self._update_schema(
            {
                "deal",
            }
        )
        if custom_fields_properties:
            self._schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a deal.",
            }

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a child context for the stream."""
        return {"deal_id": record["id"]}

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.deals.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "deals.json"


class AssociatedContacts(ZendeskSellStream):
    """Zendesk Sell asociated contacts stream class."""

    name = "associated_contacts"
    parent_stream_type = DealsStream

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.associated_contacts.list(
                deal_id=context.get("deal_id"), page=page, per_page=100  # type: ignore
            )
            if not data:
                finished = True
            for row in data:
                row["deal_id"] = context.get("deal_id")  # type: ignore
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "associated_contacts.json"
