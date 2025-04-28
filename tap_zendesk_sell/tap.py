"""Zendesk Sell tap class."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from singer_sdk import Tap
from singer_sdk import typing as th

if TYPE_CHECKING:
    from tap_zendesk_sell import streams

from tap_zendesk_sell.streams import __all__ as stream_classes

STREAM_TYPES = [
    getattr(import_module("tap_zendesk_sell.streams"), cls) for cls in stream_classes
]


class TapZendeskSell(Tap):
    """Zendesk Sell tap class."""

    name = "tap-zendesk-sell"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType(nullable=False),
            required=True,
            secret=True,
            title="Access Token",
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "device_uuid",
            th.StringType,
            required=False,
            title="Device UUID",
            description="The device's universally unique identifier (UUID)",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.ZendeskSellStream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapZendeskSell.cli()
