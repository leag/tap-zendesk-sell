"""Zendesk Sell product stream class."""

from __future__ import annotations

from typing import ClassVar

import backoff
import requests

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream


class ProductsStream(ZendeskSellStream):
    """Zendesk Sell product stream class."""

    name = "products"
    primary_keys: ClassVar[list[str]] = ["id"]

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.products.list(page=page, per_page=100)

    schema_filepath = SCHEMAS_DIR / "products.json"
