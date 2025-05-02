"""Zendesk Sell stream classes."""

from __future__ import annotations

from functools import cached_property
from http import HTTPStatus
from typing import Any, ClassVar, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.helpers.types import Context

from singer_sdk import typing as th

from tap_zendesk_sell.client import ZendeskSellStream

PropertiesList = th.PropertiesList
Property = th.Property
ObjectType = th.ObjectType
DateTimeType = th.DateTimeType
DateType = th.DateType
StringType = th.StringType
ArrayType = th.ArrayType
BooleanType = th.BooleanType
IntegerType = th.IntegerType
NumberType = th.NumberType

AddressType = ObjectType(
    Property(
        "line1",
        StringType,
        description="Line 1 of the address e.g. number, street, suite, apt #, etc.",
    ),
    Property("city", StringType, description="City name."),
    Property("postal_code", StringType, description="Zip code or equivalent."),
    Property("state", StringType, description="State name."),
    Property("country", StringType, description="Country name."),
)


class AccountsStream(ZendeskSellStream):
    """Zendesk Sell accounts stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/account/
    """

    """
    name: stream name
    path: path which will be added to api url in client.py
    schema: instream schema
    primary_keys = primary keys for the table
    replication_key = datetime keys for replication
    records_jsonpath = json response body
    """

    name = "accounts"
    path = "/accounts/self"
    primary_keys: ClassVar[list[str]] = ["id"]
    records_jsonpath = "data.[*]"
    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the account."),
        Property("name", StringType, description="Full name of the account."),
        Property(
            "currency",
            StringType,
            description=(
                "Currency of the account as the 3-character currency code in "
                "ISO4217 format."
            ),
        ),
        Property(
            "time_format",
            StringType,
            description=(
                "Time format used for the account. Either 12-hour clock 12H or "
                "24-hour clock 24H."
            ),
        ),
        Property(
            "timezone",
            StringType,
            description=(
                "Timezone of the account as the offset from Coordinated Universal "
                "Time (UTC)."
            ),
        ),
        Property(
            "phone", StringType, description="Contact phone number of the account."
        ),
        Property(
            "subdomain",
            StringType,
            description="Subdomain of the account, null for legacy accounts.",
        ),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of the account's creation.",
        ),
        Property(
            "updated_at", DateTimeType, description="Date and time of the last update."
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: int | None,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Override the default implementation to avoid adding pagination parameters
        for the '/accounts/self' endpoint, which doesn't support pagination.

        Args:
            context: Stream sync context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL parameter values.
        """
        # For the accounts/self endpoint,
        # return an empty dict as it doesn't support pagination
        return {}


class ContactsStream(ZendeskSellStream):
    """Zendesk Sell contacts stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/contacts/
    """

    name = "contacts"
    path = "/contacts"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    @cached_property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for contacts."""
        base_schema = PropertiesList(
            Property(
                "id", IntegerType, description="The unique identifier of the contact."
            ),
            Property(
                "creator_id",
                IntegerType,
                description=(
                    "The unique identifier of the user the contact was created by."
                ),
            ),
            Property(
                "owner_id",
                IntegerType,
                description=(
                    "The unique identifier of the user the contact is currently "
                    "assigned to."
                ),
            ),
            Property(
                "contact_id",
                IntegerType,
                description=(
                    "The unique identifier of the organization the contact "
                    "belongs to."
                ),
            ),
            Property(
                "parent_organization_id",
                IntegerType,
                description=(
                    "The unique identifier of an organization contact that is "
                    "parent of this organization."
                ),
            ),
            Property(
                "is_organization",
                BooleanType,
                description=(
                    "Indicator of whether or not this contact refers to an "
                    "organization or an individual."
                ),
            ),
            Property(
                "name",
                StringType,
                description=(
                    "Name of the contact. Required only if the contact is an "
                    "organization."
                ),
            ),
            Property(
                "first_name", StringType, description="First name of the contact."
            ),
            Property(
                "last_name",
                StringType,
                description=(
                    "Last name of the contact. Required only if the contact is an "
                    "individual."
                ),
            ),
            Property(
                "customer_status",
                StringType,
                description=(
                    "The customer status of the contact. "
                    "Possible values: none, current, past"
                ),
            ),
            Property(
                "prospect_status",
                StringType,
                description=(
                    "The prospect status of the contact. "
                    "Possible values: none, current, lost"
                ),
            ),
            Property("title", StringType, description="The contact's job title."),
            Property(
                "description", StringType, description="The contact's description."
            ),
            Property("industry", StringType, description="The contact's industry."),
            Property(
                "website", StringType, description="The contact's website address."
            ),
            Property("email", StringType, description="The contact's email address."),
            Property("phone", StringType, description="The contact's phone number."),
            Property(
                "mobile", StringType, description="The contact's mobile phone number."
            ),
            Property("fax", StringType, description="The contact's fax number."),
            Property(
                "twitter", StringType, description="The contact's Twitter handle."
            ),
            Property(
                "facebook", StringType, description="The contact's Facebook nickname."
            ),
            Property(
                "linkedin", StringType, description="The contact's Linkedin nickname."
            ),
            Property("skype", StringType, description="The contact's Skype nickname."),
            Property("address", AddressType, description="The contact's address."),
            Property(
                "billing_address",
                AddressType,
                description="The contact's billing address.",
            ),
            Property(
                "shipping_address",
                AddressType,
                description="The contact's shipping address.",
            ),
            Property(
                "tags",
                ArrayType(StringType),
                description="An array of tags for the contact.",
            ),
            Property(
                "custom_fields",
                ObjectType(),
                description="Custom fields data for the contact.",
            ),
            Property(
                "created_at",
                DateTimeType,
                description=(
                    "Date and time that the record was created in UTC ISO8601 format."
                ),
            ),
            Property(
                "updated_at",
                DateTimeType,
                description=(
                    "Date and time of the record's last update in UTC ISO8601 format."
                ),
            ),
        ).to_dict()

        # Add custom fields
        custom_fields_properties = self._update_schema({"contact"})
        if custom_fields_properties:
            if "properties" not in base_schema:
                base_schema["properties"] = {}
            base_schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a contact.",
                "type": ["object", "null"],
            }
        return base_schema


class DealSourcesStream(ZendeskSellStream):
    """Zendesk Sell deal sources stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/deal-sources/
    """

    name = "deal_sources"
    path = "/deal_sources"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property(
            "id", IntegerType, description="Unique identifier of the deal source."
        ),
        Property(
            "creator_id",
            IntegerType,
            description="Unique identifier of the user that created the source.",
        ),
        Property("name", StringType, description="Name of the source."),
        Property(
            "resource_type",
            StringType,
            description="Type name of the resource the source is attached to.",
        ),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of creation in UTC (ISO 8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO 8601 format).",
        ),
    ).to_dict()


class DealUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell deal unqualified reasons stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/deal-unqualified-reasons/
    """

    name = "deal_unqualified_reasons"
    path = "/deal_unqualified_reasons"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property(
            "id",
            IntegerType,
            description="Unique identifier of the deal unqualified reason.",
        ),
        Property(
            "creator_id",
            IntegerType,
            description=(
                "Unique identifier of the user that created the unqualified reason."
            ),
        ),
        Property("name", StringType, description="Name of the unqualified reason."),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of creation in UTC (ISO 8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO 8601 format).",
        ),
    ).to_dict()


class DealsStream(ZendeskSellStream):
    """Zendesk Sell deals stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/deals/
    """

    name = "deals"
    path = "/deals"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"

    @cached_property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for deals."""
        base_schema = PropertiesList(
            Property("id", IntegerType, description="Unique identifier of the deal."),
            Property(
                "creator_id",
                IntegerType,
                description="Unique identifier of the user who created the deal.",
            ),
            Property(
                "owner_id",
                IntegerType,
                description=(
                    "Unique identifier of the user that the deal is assigned to."
                ),
            ),
            Property("name", StringType, description="Name of the deal."),
            Property(
                "value",
                NumberType,
                description=(
                    "Value of the deal in a currency specified in the currency field."
                ),
            ),
            Property(
                "currency",
                StringType,
                description=(
                    "Currency of the deal, specified in 3-character currency code "
                    "(ISO4217) format."
                ),
            ),
            Property(
                "hot",
                BooleanType,
                description="Indicator of whether or not the deal is hot.",
            ),
            Property(
                "stage_id",
                IntegerType,
                description=(
                    "Unique identifier of the deal's current stage in the pipeline."
                ),
            ),
            Property(
                "last_stage_change_at",
                DateTimeType,
                description=(
                    "Date and time when the deal was moved into the current stage in "
                    "UTC (ISO8601 format)."
                ),
            ),
            Property(
                "last_stage_change_by_id",
                IntegerType,
                description=(
                    "Unique identifier of the user who moved the deal into the current "
                    "stage."
                ),
            ),
            Property(
                "last_activity_at",
                DateTimeType,
                description=(
                    "Date and time of the last activity on the deal in UTC "
                    "(ISO8601 format)."
                ),
            ),
            Property(
                "source_id", IntegerType, description="Unique identifier of the Source."
            ),
            Property(
                "loss_reason_id",
                IntegerType,
                description="Reason why the deal was lost.",
            ),
            Property(
                "unqualified_reason_id",
                IntegerType,
                description="Reason why the deal was unqualified.",
            ),
            Property(
                "contact_id",
                IntegerType,
                description="Unique identifier of a primary contact.",
            ),
            Property(
                "organization_id",
                IntegerType,
                description="Unique identifier of an organization.",
            ),
            Property(
                "estimated_close_date",
                StringType,
                description="Estimated close date of the deal.",
            ),
            Property(
                "customized_win_likelihood",
                IntegerType,
                description="User-provided win likelihood with value range 0-100.",
            ),
            Property(
                "dropbox_email",
                StringType,
                description="Dropbox email connected with the deal.",
            ),
            Property(
                "tags",
                ArrayType(StringType),
                description="An array of tags for a deal.",
            ),
            Property(
                "associated_contacts", ObjectType(), description="associated contacts."
            ),
            Property(
                "created_at",
                DateTimeType,
                description=(
                    "Date and time that the deal was created in UTC "
                    "(ISO8601 format)."
                ),
            ),
            Property(
                "updated_at",
                DateTimeType,
                description=(
                    "Date and time of the last update on the deal in UTC "
                    "(ISO8601 format)."
                ),
            ),
            Property(
                "added_at",
                DateTimeType,
                description=(
                    "Date and time that the deal was started in UTC "
                    "(ISO8601 format)."
                ),
            ),
        ).to_dict()

        # Add custom fields
        custom_fields_properties = self._update_schema({"deal"})
        if custom_fields_properties:
            if "properties" not in base_schema:
                base_schema["properties"] = {}
            base_schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a deal.",
                "type": ["object", "null"],
            }
        return base_schema

    def get_child_context(
        self, record: dict, context: Context | None  # noqa: ARG002
    ) -> dict:
        """Return a child context for the stream."""
        return {"deal_id": record["id"]}


class AssociatedContacts(ContactsStream):
    """Zendesk Sell associated contacts stream class."""

    name = "associated_contacts"
    parent_stream_type = DealsStream
    path = "/deals/{deal_id}/associated_contacts"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    def get_records(self, context: Context | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        deal_id = context.get("deal_id") if context else None
        if deal_id is None:
            self.logger.warning(
                "Skipping AssociatedContacts: missing 'deal_id' in context."
            )
            return

        # Use the standard request_records method but add deal_id to each record
        for record in super().request_records(context):
            record["deal_id"] = deal_id
            yield record

    def get_url(self, context: dict | None) -> str:
        """Get URL for API requests.

        Override this method to format the URL with the deal_id from context.

        Args:
            context: Stream partition or context dictionary.

        Returns:
            URL with deal_id interpolated.
        """
        deal_id = context.get("deal_id") if context else None
        if deal_id is None:
            msg = "deal_id is required in context"
            raise ValueError(msg)
        return self.url_base + self.path.format(deal_id=deal_id)


class EventsStream(ZendeskSellStream):
    """Zendesk Sell events stream class.

    Events are emitted when resources change in the system.
    https://developer.zendesk.com/api-reference/sales-crm/sync/introduction/
    https://developer.zendesk.com/api-reference/sales-crm/sync/protocol/
    https://developer.zendesk.com/api-reference/sales-crm/sync/requests/
    https://developer.zendesk.com/api-reference/sales-crm/sync/reference/
    """

    name = "events"
    path = "/sync"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property(
            "meta",
            ObjectType(
                Property("version", IntegerType),
                Property("type", StringType),
                Property(
                    "sync",
                    ObjectType(
                        Property("revision", IntegerType),
                        Property("event_type", StringType),
                        Property("ack_key", StringType),
                    ),
                ),
            ),
            description="Metadata about the event",
        ),
        Property(
            "data",
            ObjectType(
                Property(
                    "id", IntegerType, description="Unique identifier for the event"
                ),
                Property(
                    "resource_type",
                    StringType,
                    description="Type of resource that was modified",
                ),
                Property(
                    "resource_id",
                    IntegerType,
                    description="ID of the resource that was modified",
                ),
                Property(
                    "type",
                    StringType,
                    description="Type of change (created, updated, deleted)",
                ),
                Property(
                    "creator_id",
                    IntegerType,
                    description="User ID who performed the action",
                ),
                Property(
                    "created_at", StringType, description="When the event occurred"
                ),
                # The following fields depend on the resource_type and may be present
                Property("name", StringType, description="Resource name if available"),
                Property("value", StringType, description="Value field if available"),
                Property("currency", StringType, description="Currency if applicable"),
                Property("owner_id", IntegerType, description="Owner ID if applicable"),
                Property("email", StringType, description="Email if applicable"),
                Property("phone", StringType, description="Phone if applicable"),
                Property("address", AddressType, description="Address if applicable"),
                Property(
                    "tags", ArrayType(StringType), description="Tags if applicable"
                ),
                Property(
                    "updated_at",
                    StringType,
                    description="Update timestamp if applicable",
                ),
                # Many more fields may be present depending on the event type
            ),
            description="The event data",
        ),
    ).to_dict()

    def get_records(self, _context: dict | None = None) -> Iterable[dict]:
        """Implement Zendesk Sell Sync API v2 protocol for events."""
        device_uuid = self.config.get("device_uuid")
        if not device_uuid:
            self.logger.error("device_uuid is required for sync stream 'events'")
            return
        access_token = self.config.get("access_token")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Basecrm-Device-UUID": device_uuid,
        }
        # Start a new sync session
        timeout = getattr(self, "request_timeout", 300)
        start_url = f"{self.url_base}/sync/start"
        start_resp = requests.post(start_url, headers=headers, timeout=timeout)
        if start_resp.status_code == HTTPStatus.NO_CONTENT:
            return
        start_resp.raise_for_status()
        session = start_resp.json()
        session_id = session.get("id")
        if not session_id:
            return
        # Drain the main queue
        while True:
            fetch_url = f"{self.url_base}/sync/{session_id}/queues/main"
            fetch_resp = requests.get(fetch_url, headers=headers, timeout=timeout)
            fetch_resp.raise_for_status()
            items = fetch_resp.json().get("items", [])
            if not items:
                break
            ack_keys: list[str] = []
            for item in items:
                yield item.get("data", {})
                key = item.get("meta", {}).get("sync", {}).get("ack_key")
                if key:
                    ack_keys.append(key)
            # Acknowledge processed events
            if ack_keys:
                ack_url = f"{self.url_base}/sync/ack"
                ack_body = {"ack_keys": ack_keys}
                ack_resp = requests.post(
                    ack_url,
                    json=ack_body,
                    headers=headers,
                    timeout=timeout,
                )
                ack_resp.raise_for_status()


class LeadSourcesStream(ZendeskSellStream):
    """Zendesk Sell lead sources stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/lead-sources/
    """

    name = "lead_sources"
    path = "/lead_sources"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property(
            "id", IntegerType, description="Unique identifier of the lead source."
        ),
        Property(
            "creator_id",
            IntegerType,
            description="Unique identifier of the user that created the source.",
        ),
        Property("name", StringType, description="Name of the source."),
        Property(
            "resource_type",
            StringType,
            description="Type name of the resource the source is attached to.",
        ),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of creation in UTC (ISO 8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO 8601 format).",
        ),
    ).to_dict()


class LeadUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell lead unqualified reasons stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/lead-unqualified-reasons/
    """

    name = "lead_unqualified_reasons"
    path = "/lead_unqualified_reasons"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property(
            "id",
            IntegerType,
            description="Unique identifier of the lead unqualified reason.",
        ),
        Property("name", StringType, description="Name of the unqualified reason."),
        Property(
            "creator_id",
            IntegerType,
            description=(
                "Unique identifier of the user that created the unqualified reason."
            ),
        ),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of creation in UTC (ISO 8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO 8601 format).",
        ),
    ).to_dict()


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/leads/
    """

    name = "leads"
    path = "/leads"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"

    @cached_property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for leads."""
        base_schema = PropertiesList(
            Property("id", IntegerType, description="Unique identifier of the lead."),
            Property(
                "creator_id",
                IntegerType,
                description="Unique identifier of the user who created the lead.",
            ),
            Property(
                "owner_id",
                IntegerType,
                description=(
                    "Unique identifier of the user who currently owns the lead."
                ),
            ),
            Property("first_name", StringType, description="First name of the lead."),
            Property(
                "last_name",
                StringType,
                description=(
                    "Last name of the lead. Required unless organization_name field "
                    "is provided."
                ),
            ),
            Property(
                "organization_name",
                StringType,
                description=(
                    "Organization name of the lead. Required unless last_name field "
                    "is provided."
                ),
            ),
            Property("status", StringType, description="Status of the lead."),
            Property(
                "source_id", IntegerType, description="Unique identifier of the Source."
            ),
            Property("title", StringType, description="Job title of the lead."),
            Property("description", StringType, description="Lead description."),
            Property("industry", StringType, description="Organization's industry."),
            Property("website", StringType, description="Lead's website."),
            Property("email", StringType, description="Lead's email."),
            Property("phone", StringType, description="Lead's phone number."),
            Property("mobile", StringType, description="Lead's mobile phone number."),
            Property("fax", StringType, description="Lead's fax number."),
            Property("twitter", StringType, description="Lead's Twitter handle."),
            Property("facebook", StringType, description="Lead's Facebook nickname."),
            Property("linkedin", StringType, description="Lead's Linkedin nickname."),
            Property("skype", StringType, description="Lead's Skype nickname."),
            Property("address", AddressType, description="The lead's address."),
            Property(
                "tags",
                ArrayType(StringType),
                description="An array of tags for a lead. See more at Tags.",
            ),
            Property(
                "unqualified_reason_id",
                IntegerType,
                description="Reason why the lead was unqualified.",
            ),
            Property(
                "created_at",
                DateTimeType,
                description="Date and time of the creation in UTC (ISO8601 format).",
            ),
            Property(
                "updated_at",
                DateTimeType,
                description="Date and time of the last update in UTC (ISO8601 format).",
            ),
        ).to_dict()

        # Add custom fields
        custom_fields_properties = self._update_schema({"lead"})
        if custom_fields_properties:
            if "properties" not in base_schema:
                base_schema["properties"] = {}
            base_schema["properties"]["custom_fields"] = {
                "properties": custom_fields_properties,
                "description": "Custom fields attached to a lead.",
                "type": ["object", "null"],
            }
        return base_schema


class LossReasonsStream(ZendeskSellStream):
    """Zendesk Sell loss reasons stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/loss-reasons/
    """

    name = "loss_reasons"
    path = "/loss_reasons"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the loss reason"),
        Property(
            "creator_id",
            IntegerType,
            description="Unique identifier of the user who created the loss reason",
        ),
        Property("name", StringType, description="Explanation of the loss reason"),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time when the loss reason was created",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time when the loss reason was last updated",
        ),
    ).to_dict()


class NotesStream(ZendeskSellStream):
    """Zendesk Sell notes stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/notes/
    """

    name = "notes"
    path = "/notes"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="The unique identifier of the note"),
        Property(
            "creator_id",
            IntegerType,
            description="The unique identifier of the creator of the note",
        ),
        Property(
            "resource_type",
            StringType,
            description="The type of resource the note is attached to",
        ),
        Property(
            "resource_id",
            IntegerType,
            description="The unique identifier of the resource the note is attached to",
        ),
        Property("content", StringType, description="The content of the note"),
        Property(
            "is_important",
            BooleanType,
            description="Whether the note is important or not",
        ),
        Property("tags", ArrayType(StringType), description="The tags of the note"),
        Property(
            "created_at",
            DateTimeType,
            description="The date and time the note was created",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="The date and time the note was last updated",
        ),
        Property(
            "type",
            StringType,
            description=(
                "The type of permission of the note, e.g. 'regular' or 'restricted'."
            ),
        ),
    ).to_dict()


class OrdersStream(ZendeskSellStream):
    """Zendesk Sell orders stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/orders/
    """

    name = "orders"
    path = "/orders"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the order."),
        Property(
            "deal_id",
            IntegerType,
            description="Id of the deal the order is associated to.",
        ),
        Property(
            "discount",
            IntegerType,
            description="Discount on the whole order in percents.",
        ),
        Property(
            "created_at",
            DateTimeType,
            description=(
                "Date and time that the order was created in UTC (ISO8601 format)."
            ),
        ),
        Property(
            "updated_at",
            DateTimeType,
            description=(
                "Date and time that the order was updated in UTC (ISO8601 format)."
            ),
        ),
    ).to_dict()

    def get_child_context(
        self, record: dict, context: dict | None = None  # noqa: ARG002
    ) -> dict:
        """Return a child context for the stream."""
        return {
            "order_id": record["id"],
        }


class LineItemsStream(ZendeskSellStream):
    """Zendesk Sell line items stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/line_items/
    """

    name = "line_items"
    parent_stream_type = OrdersStream
    path = "/orders/{order_id}/line_items"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property(
            "order_id", IntegerType, description="The unique identifier for the order."
        ),
        Property(
            "line_item_id",
            IntegerType,
            description="Unique identifier of the line item.",
        ),
        Property(
            "name",
            StringType,
            description="Name of the product. Value is copied from the product.",
        ),
        Property(
            "sku",
            StringType,
            description=(
                "Stock Keeping Unit identification code. "
                "Value is copied from the product."
            ),
        ),
        Property(
            "description",
            StringType,
            description="Description of the product. Value is copied from the product.",
        ),
        Property(
            "value",
            NumberType,
            description=(
                "Value of one unit of the product. "
                "It is product's price after applying markup."
            ),
        ),
        Property(
            "variation",
            NumberType,
            description=(
                "Variation of the product's price for this line item. "
                "Value of 5 means that 5% markup is added, -10 means there is a "
                "10% discount."
            ),
        ),
        Property(
            "price",
            NumberType,
            description=(
                "Price of one unit of the product. Value is copied from the product."
            ),
        ),
        Property(
            "currency",
            StringType,
            description=(
                "Currency of value and price, specified in 3-character currency code "
                "(ISO4217) format."
            ),
        ),
        Property(
            "quantity",
            IntegerType,
            description=(
                "Quantity of the product included in this line item. "
                "Default value is 1."
            ),
        ),
        Property(
            "created_at",
            DateTimeType,
            description=(
                "Date and time that the associated contact was created in UTC "
                "(ISO4217 format)."
            ),
        ),
        Property(
            "updated_at",
            DateTimeType,
            description=(
                "Date and time of the last update on the associated contact in UTC "
                "(ISO4217 format)."
            ),
        ),
    ).to_dict()

    def get_records(self, context: dict | None = None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        order_id = context.get("order_id") if context else None
        if order_id is None:
            self.logger.warning("Skipping LineItems: missing 'order_id' in context.")
            return

        # Use the standard request_records method but add order_id to each record
        for record in super().request_records(context):
            record["order_id"] = order_id
            yield record

    def get_url(self, context: dict | None) -> str:
        """Get URL for API requests.

        Override this method to format the URL with the order_id from context.

        Args:
            context: Stream partition or context dictionary.

        Returns:
            URL with order_id interpolated.
        """
        order_id = context.get("order_id") if context else None
        if order_id is None:
            msg = "order_id is required in context"
            raise ValueError(msg)
        return self.url_base + self.path.format(order_id=order_id)


class PipelinesStream(ZendeskSellStream):
    """Zendesk Sell pipelines stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/pipelines/
    """

    name = "pipelines"
    path = "/pipelines"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the pipeline."),
        Property("name", StringType, description="Name of the pipeline."),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of the creation in UTC (ISO8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO8601 format).",
        ),
    ).to_dict()


class ProductsStream(ZendeskSellStream):
    """Zendesk Sell products stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/products/
    """

    name = "products"
    path = "/products"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the product."),
        Property(
            "creator_id",
            IntegerType,
            description="Unique identifier of the user who created the product.",
        ),
        Property("name", StringType, description="Name of the product."),
        Property(
            "sku", StringType, description="Stock Keeping Unit identification code."
        ),
        Property("description", StringType, description="Description of the product."),
        Property("active", BooleanType, description="If true, the product is active."),
        Property(
            "max_discount",
            NumberType,
            description="Maximum discount that can be applied to the product.",
        ),
        Property(
            "max_markup",
            NumberType,
            description="Maximum markup that can be applied to the product.",
        ),
        Property("cost", NumberType, description="Cost of the product."),
        Property(
            "cost_currency",
            StringType,
            description=(
                "Currency of the cost, specified in 3-character "
                "currency code (ISO4217) format."
            ),
        ),
        Property(
            "prices",
            ArrayType(
                ObjectType(
                    Property("amount", NumberType, description="Price of the product."),
                    Property(
                        "currency",
                        StringType,
                        description=(
                            "Currency of the price, specified in "
                            "3-character currency code (ISO4217) format."
                        ),
                    ),
                )
            ),
            description="Prices of the product in different currencies.",
        ),
        Property(
            "created_at",
            DateTimeType,
            description=(
                "Date and time that the product was created in UTC (ISO8601 format)."
            ),
        ),
        Property(
            "updated_at",
            DateTimeType,
            description=(
                "Date and time of the last update on the product in UTC "
                "(ISO8601 format)."
            ),
        ),
    ).to_dict()


class StagesStream(ZendeskSellStream):
    """Zendesk Sell stages stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/stages/
    """

    name = "stages"
    path = "/stages"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the stage."),
        Property("name", StringType, description="Name of the stage."),
        Property(
            "category",
            StringType,
            description=(
                "Category of the stage. Possible values: incoming, qualified, "
                "won, lost, unqualified."
            ),
        ),
        Property(
            "likelihood",
            IntegerType,
            description=(
                "Probability of deal closing in this stage, expressed as percentage."
            ),
        ),
        Property(
            "active", BooleanType, description="Whether or not the stage is active."
        ),
        Property(
            "pipeline_id",
            IntegerType,
            description="Unique identifier of the pipeline the stage belongs to.",
        ),
        Property(
            "position",
            IntegerType,
            description="Position of the stage in the pipeline.",
        ),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of the creation in UTC (ISO8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO8601 format).",
        ),
    ).to_dict()


class TagsStream(ZendeskSellStream):
    """Zendesk Sell tags stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/tags/
    """

    name = "tags"
    path = "/tags"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the tag."),
        Property("name", StringType, description="Name of the tag."),
        Property(
            "resource_type",
            StringType,
            description="Type of resources the tag can be applied to.",
        ),
        Property(
            "creator_id",
            IntegerType,
            description="Unique identifier of the user who created the tag.",
        ),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of the creation in UTC (ISO8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO8601 format).",
        ),
    ).to_dict()


class TasksStream(ZendeskSellStream):
    """Zendesk Sell tasks stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/tasks/
    """

    name = "tasks"
    path = "/tasks"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the task."),
        Property(
            "creator_id",
            IntegerType,
            description="Unique identifier of the user who created the task.",
        ),
        Property(
            "owner_id",
            IntegerType,
            description="Unique identifier of the user the task is assigned to.",
        ),
        Property(
            "resource_id",
            IntegerType,
            description=(
                "Unique identifier of the resource this task is associated with."
            ),
        ),
        Property(
            "resource_type",
            StringType,
            description="Type of the resource this task is associated with.",
        ),
        Property(
            "completed",
            BooleanType,
            description="Whether or not the task has been completed.",
        ),
        Property(
            "completed_at",
            DateTimeType,
            description="Date and time the task was completed in UTC (ISO8601 format).",
        ),
        Property("due_date", DateTimeType, description="Date the task is due."),
        Property(
            "overdue", BooleanType, description="Whether or not the task is overdue."
        ),
        Property(
            "remind_at",
            DateTimeType,
            description="Date and time of the reminder in UTC (ISO8601 format).",
        ),
        Property("content", StringType, description="Content of the task."),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of the creation in UTC (ISO8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO8601 format).",
        ),
    ).to_dict()


class TextMessagesStream(ZendeskSellStream):
    """Zendesk Sell text messages stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/text_messages/
    """

    name = "text_messages"
    path = "/text_messages"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property(
            "id", IntegerType, description="Unique identifier of the text message."
        ),
        Property(
            "creator_id",
            IntegerType,
            description="Unique identifier of the user who created the text message.",
        ),
        Property(
            "resource_id",
            IntegerType,
            description=(
                "Unique identifier of the resource this text message is associated "
                "with."
            ),
        ),
        Property(
            "resource_type",
            StringType,
            description="Type of the resource this text message is associated with.",
        ),
        Property(
            "phone_number",
            StringType,
            description="The phone number the text message was sent to.",
        ),
        Property("content", StringType, description="Content of the text message."),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of the creation in UTC (ISO8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO8601 format).",
        ),
    ).to_dict()


class UsersStream(ZendeskSellStream):
    """Zendesk Sell users stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/users/
    """

    name = "users"
    path = "/users"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the user."),
        Property("name", StringType, description="Full name of the user."),
        Property("email", StringType, description="Email address of the user."),
        Property(
            "role",
            StringType,
            description="Role of the user. Possible values: user, admin.",
        ),
        Property(
            "status",
            StringType,
            description="Status of the user. Possible values: active, inactive.",
        ),
        Property("reports_to", IntegerType, description="ID of the user's manager."),
        Property(
            "group",
            ObjectType(
                Property("id", IntegerType, description="ID of the user's group."),
                Property("name", StringType, description="Name of the user's group."),
            ),
            description="Group this user belongs to.",
        ),
        Property(
            "team_name",
            StringType,
            description="Name of the team this user belongs to.",
        ),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of the creation in UTC (ISO8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO8601 format).",
        ),
    ).to_dict()


class VisitOutcomesStream(ZendeskSellStream):
    """Zendesk Sell visit outcomes stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/visit_outcomes/
    """

    name = "visit_outcomes"
    path = "/visit_outcomes"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property(
            "id", IntegerType, description="Unique identifier of the visit outcome."
        ),
        Property("name", StringType, description="Name of the visit outcome."),
        Property(
            "created_at",
            DateTimeType,
            description="Date and time of the creation in UTC (ISO8601 format).",
        ),
        Property(
            "updated_at",
            DateTimeType,
            description="Date and time of the last update in UTC (ISO8601 format).",
        ),
    ).to_dict()


class VisitsStream(ZendeskSellStream):
    """Zendesk Sell visits stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/visits/
    """

    name = "visits"
    path = "/visits"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the visit."),
        Property(
            "creator_id",
            IntegerType,
            description="Unique identifier of the user who created the visit.",
        ),
        Property(
            "resource_type",
            StringType,
            description="Type of the resource this visit is associated with.",
        ),
        Property(
            "resource_id",
            IntegerType,
            description=(
                "Unique identifier of the resource this visit is associated with."
            ),
        ),
        Property(
            "user_id",
            IntegerType,
            description="Unique identifier of the user who performed the visit.",
        ),
        Property(
            "outcome_id",
            IntegerType,
            description="Unique identifier of the visit outcome.",
        ),
        Property("summary", StringType, description="Summary or title of the visit."),
        Property("date", DateType, description="Date of the visit."),
        Property(
            "created_at",
            DateTimeType,
            description=(
                "Date and time when the visit was created in UTC (ISO8601 format)."
            ),
        ),
        Property(
            "updated_at",
            DateTimeType,
            description=(
                "Date and time when the visit was last updated in UTC "
                "(ISO8601 format)."
            ),
        ),
    ).to_dict()


__all__ = [
    "AccountsStream",
    "AssociatedContacts",
    "ContactsStream",
    "DealSourcesStream",
    "DealUnqualifiedReasonsStream",
    "DealsStream",
    "EventsStream",
    "LeadSourcesStream",
    "LeadUnqualifiedReasonsStream",
    "LeadsStream",
    "LineItemsStream",
    "LossReasonsStream",
    "NotesStream",
    "OrdersStream",
    "PipelinesStream",
    "ProductsStream",
    "StagesStream",
    "TagsStream",
    "TasksStream",
    "TextMessagesStream",
    "UsersStream",
    "VisitOutcomesStream",
    "VisitsStream",
]
