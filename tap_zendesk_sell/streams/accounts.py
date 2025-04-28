"""Zendesk Sell account stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR

if TYPE_CHECKING:
    from collections.abc import Iterable


class AccountsStream(ZendeskSellStream):
    """Zendesk Sell account stream class."""

    name = "accounts"
    primary_keys: ClassVar[list[str]] = ["id"]

    def get_records(self, _context: dict | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        row = self.conn.accounts.self()
        if row:
            yield row

    schema_filepath = SCHEMAS_DIR / "accounts.json"
