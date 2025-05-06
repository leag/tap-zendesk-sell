"""Zendesk Sell tap class."""

from __future__ import annotations

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_zendesk_sell import streams


class TapZendeskSell(Tap):
    """Zendesk Sell tap class."""

    name = "tap-zendesk-sell"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            required=True,
            secret=True,
            description="Provides access to Zendesk Sell API",
            title="Access Token",
        ),
        th.Property(
            "device_uuid",
            th.StringType,
            required=False,
            description="Identifier used accross sync sessions",
            title="Device UUID",
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [
            streams.AccountsStream(self),
            streams.AssociatedContacts(self),
            streams.ContactsStream(self),
            streams.DealSourcesStream(self),
            streams.DealUnqualifiedReasonsStream(self),
            streams.DealsStream(self),
            streams.LeadSourcesStream(self),
            streams.LeadsStream(self),
            streams.LeadUnqualifiedReasonsStream(self),
            streams.LineItemsStream(self),
            streams.LossReasonsStream(self),
            streams.NotesStream(self),
            streams.OrdersStream(self),
            streams.PipelinesStream(self),
            streams.ProductsStream(self),
            streams.StagesStream(self),
            streams.SyncStream(self),
            streams.TagsStream(self),
            streams.TasksStream(self),
            streams.TextMessagesStream(self),
            streams.UsersStream(self),
            streams.VisitOutcomesStream(self),
            streams.VisitsStream(self),
        ]
