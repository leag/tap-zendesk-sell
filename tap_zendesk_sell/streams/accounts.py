"""Zendesk Sell account stream class."""

from collections.abc import Iterable
from typing import Optional

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class AccountsStream(ZendeskSellStream):
    """Zendesk Sell account stream class."""

    name = "accounts"
    primary_keys = ["id"]

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        row = self.conn.accounts.self()
        if row:
            yield row

    schema_filepath = SCHEMAS_DIR / "accounts.json"
