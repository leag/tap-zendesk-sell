"""Zendesk Sell tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_zendesk_sell.streams import SyncStream, ContactsStream

STREAM_TYPES = [SyncStream, ContactsStream]


class TapZendeskSell(Tap):
    """Zendesk Sell tap class."""

    name = "tap-zendesk_sell"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "device_uuid",
            th.StringType,
            required=True,
            description="The device's universally unique identifier (UUID)",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
