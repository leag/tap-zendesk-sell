"""Zendesk Sell product stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable


class ProductsStream(ZendeskSellStream):
    """Zendesk Sell product stream class."""

    name = "products"
    primary_keys: ClassVar[list[str]] = ["id"]

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        while True:
            data = self.conn.products.list(per_page=100, page=page, sort_by="id")
            if not data:
                break
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "products.json"
