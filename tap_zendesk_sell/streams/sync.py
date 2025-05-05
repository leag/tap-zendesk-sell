"""Stream type classes for tap-zendesk-sell."""

import uuid
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

    def get_device_uuid(self) -> str:
        """Return the device UUID.

        From the stream state if it has it, otherwise from the config.
        If neither have it, generate a new UUID and save it to the state.
        """
        if self.get_context_state(None).get("device_uuid"):
            return self.get_context_state(None)["device_uuid"]
        if self.config.get("device_uuid"):
            self.get_context_state(None)["device_uuid"] = self.config["device_uuid"]
            return self.config["device_uuid"]
        self.logger.info("Generating a device UUID")
        device_uuid = str(uuid.uuid4())
        self.get_context_state(None)["device_uuid"] = device_uuid
        return device_uuid

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        session = self.conn.sync.start(self.get_device_uuid())
        finished = False
        if session is None or "id" not in session:
            finished = True
        while not finished:
            queue_items = self.conn.sync.fetch(self.get_device_uuid(), session["id"])
            if not queue_items:
                finished = True
            ack_keys = []
            for item in queue_items:
                ack_keys.append(item["meta"]["sync"]["ack_key"])
                yield {"data": item["data"], "meta": item["meta"]}
            if ack_keys:
                self.conn.sync.ack(self.get_device_uuid(), ack_keys)

    schema_filepath = SCHEMAS_DIR / "events.json"
