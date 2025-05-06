"""Zendesk Sell orders stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable


class OrdersStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

    name = "orders"
    primary_keys = ("id",)

    def get_child_context(self, record: dict, _context: dict | None) -> dict:
        """Return a child context for the record."""
        return {"order_id": record["id"]}

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.orders.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
            yield from data
            page += 1

    schema_filepath = SCHEMAS_DIR / "orders.json"


class LineItemsStream(ZendeskSellStream):
    """Zendesk Sell line items stream class."""

    name = "line_items"
    parent_stream_type = OrdersStream

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.line_items.list(
                order_id=context.get("order_id"),
                per_page=100,
                page=page,
                sort_by="updated_at",
            )
            if not data:
                finished = True
            for row in data:
                row["line_item_id"] = row.pop("id")
                row["order_id"] = context.get("order_id")
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "line_items.json"
