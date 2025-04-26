"""ZendeskSell entry point."""

from __future__ import annotations

from tap_zendesk_sell.tap import TapZendeskSell

TapZendeskSell.cli()
