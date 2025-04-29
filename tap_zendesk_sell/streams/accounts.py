"""Zendesk Sell account stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.helpers.types import Context


class AccountsStream(ZendeskSellStream):
    """Zendesk Sell account stream class."""

    name = "accounts"
    primary_keys: ClassVar[list[str]] = ["id"]

    def get_records(self, context: Context | None) -> Iterable[dict]:  # noqa: ARG002
        """Return a generator of row-type dictionary objects."""
        yield self.conn.accounts.self()

    schema_filepath = SCHEMAS_DIR / "accounts.json"
