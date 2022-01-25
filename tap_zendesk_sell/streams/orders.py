"""Zendesk Sell orders stream class."""
from typing import Iterable, Optional

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class OrdersStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

    name = "orders"
    primary_keys = ["id"]

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a child context for the record."""
        return {"order_id": record["id"]}

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.orders.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
            for row in data:
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "orders.json"


class LineItemsStream(ZendeskSellStream):
    """Zendesk Sell line items stream class."""

    name = "line_items"
    parent_stream_type = OrdersStream

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.line_items.list(
                order_id=context.get("order_id"),  # type: ignore
                per_page=100,
                page=page,
                sort_by="updated_at",
            )
            if not data:
                finished = True
            for row in data:
                row["line_item_id"] = row.pop("id")
                row["order_id"] = context.get("order_id")  # type: ignore
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "line_items.json"
