"""Stream type classes for tap-zendesk_sell."""

from typing import Iterable, Optional

from singer_sdk.tap_base import Tap

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class SyncStream(ZendeskSellStream):
    """Zendesk Sell sync stream class."""

    name = "events"

    def __init__(self, tap: Tap):
        """Initialize the stream."""
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
