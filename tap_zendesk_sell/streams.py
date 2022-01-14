"""Stream type classes for tap-zendesk_sell."""

from pathlib import Path
from typing import Iterable, Optional

from singer_sdk.tap_base import Tap

from tap_zendesk_sell.client import ZendeskSellStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class SyncStream(ZendeskSellStream):
    name = "events"

    def __init__(self, tap: Tap):
        super().__init__(tap)
        custom_fields_properties = self._update_schema()
        if custom_fields_properties:
            self._schema["properties"]["data"]["properties"]["custom_fields"] = {
                "properties": custom_fields_properties
            }

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""

        session = self.conn.sync.start(self.config.get("device_uuid"))
        finished = False
        if session is None or "id" not in session:
            finished = True
        while not finished:
            queue_items = self.conn.sync.fetch(
                self.config.get("device_uuid"), session["id"]
            )
            if not queue_items:
                finished = True
            ack_keys = []
            for item in queue_items:
                ack_keys.append(item["meta"]["sync"]["ack_key"])
                yield {"data": item["data"], "meta": item["meta"]}
            if ack_keys:
                self.conn.sync.ack(self.config.get("device_uuid"), ack_keys)

    schema_filepath = SCHEMAS_DIR / "events.json"


class ContactsStream(ZendeskSellStream):
    name = "contacts"

    def __init__(self, tap: Tap):
        super().__init__(tap)
        custom_fields_properties = self._update_schema(
            {
                "contact",
            }
        )
        if custom_fields_properties:
            self._schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a contact.",
            }

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.contacts.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
            for row in data:
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "contacts.json"
