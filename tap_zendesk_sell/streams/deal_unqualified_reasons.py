"""Zendesk Sell deal sources stream class."""

from __future__ import annotations

from typing import ClassVar

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream


class DealUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell deal unqualified reasons stream class."""

    name = "deal_unqualified_reasons"
    primary_keys: ClassVar[list[str]] = ["id"]


    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.deal_unqualified_reasons.list(page=page)

    schema_filepath = SCHEMAS_DIR / "deal_unqualified_reasons.json"
