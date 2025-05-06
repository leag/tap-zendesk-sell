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
            streams.AccountsStream,
            streams.AssociatedContacts,
            streams.ContactsStream,
            streams.DealSourcesStream,
            streams.DealUnqualifiedReasonsStream,
            streams.DealsStream,
            streams.LeadSourcesStream,
            streams.LeadsStream,
            streams.LeadUnqualifiedReasonsStream,
            streams.LineItemsStream,
            streams.LossReasonsStream,
            streams.NotesStream,
            streams.OrdersStream,
            streams.PipelinesStream,
            streams.ProductsStream,
            streams.StagesStream,
            streams.SyncStream,
            streams.TagsStream,
            streams.TasksStream,
            streams.TextMessagesStream,
            streams.UsersStream,
            streams.VisitOutcomesStream,
            streams.VisitsStream,
        ]
