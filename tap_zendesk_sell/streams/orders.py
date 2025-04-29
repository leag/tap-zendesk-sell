"""Zendesk Sell orders stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import backoff
import requests

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.helpers.types import Context


class OrdersStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

    name = "orders"
    primary_keys: ClassVar[list[str]] = ["id"]

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.orders.list(page=page, per_page=100)

    def get_child_context(
        self, record: dict, context: Context | None  # noqa: ARG002
    ) -> dict:
        """Return a child context for the record."""
        return {"order_id": record["id"]}

    schema_filepath = SCHEMAS_DIR / "orders.json"


class LineItemsStream(ZendeskSellStream):
    """Zendesk Sell line items stream class."""

    name = "line_items"
    parent_stream_type = OrdersStream

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(
        self,
        order_id: int,
        page: int,
        sort_by: str = "updated_at",
    ) -> list:
        """List line items for a specific order."""
        return self.conn.line_items.list(
            order_id=order_id,
            per_page=100,
            page=page,
            sort_by=sort_by,
        )

    def get_records(self, context: Context | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        order_id = context.get("order_id") if context else None
        if order_id is None:
            self.logger.warning(
                "Skipping LineItemsStream: missing 'order_id' in context."
            )
            return

        while True:
            data = self.list_data(order_id=order_id, page=page)
            if not data:
                break
            for row in data:
                row["line_item_id"] = row.pop("id")
                row["order_id"] = order_id
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "line_items.json"
