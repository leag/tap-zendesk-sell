"""Zendesk Sell deal sources stream class."""

from __future__ import annotations

from typing import ClassVar

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream


class DealSourcesStream(ZendeskSellStream):
    """Zendesk Sell deal sources stream class."""

    name = "deal_sources"
    primary_keys: ClassVar[list[str]] = ["id"]


    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.deal_sources.list(page=page, per_page=100)

    schema_filepath = SCHEMAS_DIR / "deal_sources.json"
