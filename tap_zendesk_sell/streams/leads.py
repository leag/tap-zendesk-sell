"""Zendesk Sell leads stream class."""
from typing import Iterable, Optional

from singer_sdk.tap_base import Tap

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR
from tenacity import retry, stop_after_attempt, wait_exponential


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

    name = "leads"
    primary_keys = ["id"]

    def __init__(self, tap: Tap):
        """Initialize the stream."""
        super().__init__(tap)
        custom_fields_properties = self._update_schema(
            {
                "lead",
            }
        )
        if custom_fields_properties:
            self._schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a lead.",
            }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def list_data(self, per_page: int, page: int) -> list:
        """List data from the API."""
        return self.conn.leads.list(per_page=per_page, page=page, sort_by="id")

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.list_data(per_page=100, page=page)
            if not data:
                finished = True
            for row in data:
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "leads.json"
