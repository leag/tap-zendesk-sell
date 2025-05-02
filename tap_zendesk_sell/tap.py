"""Zendesk Sell tap class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from singer_sdk import Tap
from singer_sdk import typing as th

if TYPE_CHECKING:
    from tap_zendesk_sell.streams import ZendeskSellStream

from tap_zendesk_sell import streams


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

    def discover_streams(self) -> list[ZendeskSellStream]:
        """Return a list of discovered streams."""
        return [
            streams.AccountsStream(self),
            streams.AssociatedContacts(self),
            streams.ContactsStream(self),
            streams.DealSourcesStream(self),
            streams.DealUnqualifiedReasonsStream(self),
            streams.DealsStream(self),
            streams.EventsStream(self),
            streams.LeadSourcesStream(self),
            streams.LeadUnqualifiedReasonsStream(self),
            streams.LeadsStream(self),
            streams.LineItemsStream(self),
            streams.LossReasonsStream(self),
            streams.NotesStream(self),
            streams.OrdersStream(self),
            streams.PipelinesStream(self),
            streams.ProductsStream(self),
            streams.StagesStream(self),
            streams.TagsStream(self),
            streams.TasksStream(self),
            streams.TextMessagesStream(self),
            streams.UsersStream(self),
            streams.VisitOutcomesStream(self),
            streams.VisitsStream(self),
        ]


if __name__ == "__main__":
    TapZendeskSell.cli()
