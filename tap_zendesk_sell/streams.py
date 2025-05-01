"""Zendesk Sell stream classes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional

import backoff
import requests

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

from singer_sdk import typing as th

from tap_zendesk_sell import SCHEMAS_DIR
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
    Property("line1", StringType, description="Line 1 of the address e.g. number, street, suite, apt #, etc."),
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
    schema = PropertiesList(
        Property("id", IntegerType, description="Unique identifier of the account."),
        Property("name", StringType, description="Full name of the account."),
        Property("currency", StringType, description="Currency of the account as the 3-character currency code in ISO4217 format."),
        Property("time_format", StringType, description="Time format used for the account. Either 12-hour clock 12H or 24-hour clock 24H."),
        Property("timezone", StringType, description="Timezone of the account as the offset from Coordinated Universal Time (UTC)."),
        Property("phone", StringType, description="Contact phone number of the account."),
        Property("subdomain", StringType, description="Subdomain of the account, null for legacy accounts."),
        Property("created_at", DateTimeType, description="Date and time of the account's creation."),
        Property("updated_at", DateTimeType, description="Date and time of the last update."),
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
        # For the accounts/self endpoint, return an empty dict as it doesn't support pagination
        return {}


class ContactsStream(ZendeskSellStream):
    """Zendesk Sell contacts stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/contacts/
    """

    name = "contacts"
    path = "/contacts"
    records_jsonpath = "$.items[*].data"  # API returns items array with data objects
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"  # Use updated_at for incremental replication

    @property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for contacts."""
        base_schema = PropertiesList(
            Property("id", IntegerType, description="The unique identifier of the contact."),
            Property("creator_id", IntegerType, description="The unique identifier of the user the contact was created by."),
            Property("owner_id", IntegerType, description="The unique identifier of the user the contact is currently assigned to."),
            Property("contact_id", IntegerType, description="The unique identifier of the organization the contact belongs to."),
            Property("parent_organization_id", IntegerType, description="The unique identifier of an organization contact that is parent of this organization."),
            Property("is_organization", BooleanType, description="Indicator of whether or not this contact refers to an organization or an individual."),
            Property("name", StringType, description="Name of the contact. Required only if the contact is an organization."),
            Property("first_name", StringType, description="First name of the contact."),
            Property("last_name", StringType, description="Last name of the contact. Required only if the contact is an individual."),
            Property("customer_status", StringType, description="The customer status of the contact. Possible values: none, current, past"),
            Property("prospect_status", StringType, description="The prospect status of the contact. Possible values: none, current, lost"),
            Property("title", StringType, description="The contact's job title."),
            Property("description", StringType, description="The contact's description."),
            Property("industry", StringType, description="The contact's industry."),
            Property("website", StringType, description="The contact's website address."),
            Property("email", StringType, description="The contact's email address."),
            Property("phone", StringType, description="The contact's phone number."),
            Property("mobile", StringType, description="The contact's mobile phone number."),
            Property("fax", StringType, description="The contact's fax number."),
            Property("twitter", StringType, description="The contact's Twitter handle."),
            Property("facebook", StringType, description="The contact's Facebook nickname."),
            Property("linkedin", StringType, description="The contact's Linkedin nickname."),
            Property("skype", StringType, description="The contact's Skype nickname."),
            Property("address", AddressType, description="The contact's address."),
            Property("billing_address", AddressType, description="The contact's billing address."),
            Property("shipping_address", AddressType, description="The contact's shipping address."),
            Property("tags", ArrayType(StringType), description="An array of tags for the contact."),
            Property("custom_fields", ObjectType(), description="Custom fields data for the contact."),
            Property("created_at", DateTimeType, description="Date and time that the record was created in UTC ISO8601 format."),
            Property("updated_at", DateTimeType, description="Date and time of the record's last update in UTC ISO8601 format."),
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

    def get_child_context(self, record: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Return a context dictionary for child streams."""
        return {
            "contact_id": record["id"],
        }


class DealSourcesStream(ZendeskSellStream):
    """Zendesk Sell deal sources stream class."""

    name = "deal_sources"
    path = "/deal_sources"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class DealUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell deal unqualified reasons stream class."""

    name = "deal_unqualified_reasons"
    path = "/deal_unqualified_reasons"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class DealsStream(ZendeskSellStream):
    """Zendesk Sell deals stream class."""

    name = "deals"
    path = "/deals"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"

    @property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for deals."""
        base_schema = super().schema
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


class AssociatedContacts(ZendeskSellStream):
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

    def get_url(self, context: Optional[dict]) -> str:
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
    """Zendesk Sell events stream class."""

    name = "events"
    path = "/sync/events"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: int | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: Stream sync context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL parameter values.
        """
        params = super().get_url_params(context, next_page_token)

        # Add the device_uuid parameter for the sync API
        device_uuid = self.config.get("device_uuid")
        if device_uuid:
            params["device_uuid"] = device_uuid

        return params


class LeadSourcesStream(ZendeskSellStream):
    """Zendesk Sell lead sources stream class."""

    name = "lead_sources"
    path = "/lead_sources"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class LeadUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell lead unqualified reasons stream class."""

    name = "lead_unqualified_reasons"
    path = "/lead_unqualified_reasons"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

    name = "leads"
    path = "/leads"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"

    @property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for leads."""
        base_schema = super().schema
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
    """Zendesk Sell loss reasons stream class."""

    name = "loss_reasons"
    path = "/loss_reasons"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class NotesStream(ZendeskSellStream):
    """Zendesk Sell notes stream class."""

    name = "notes"
    path = "/notes"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class OrdersStream(ZendeskSellStream):
    """Zendesk Sell orders stream class."""

    name = "orders"
    path = "/orders"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"

    def get_child_context(self, record: dict, context: Optional[dict] = None) -> dict:
        """Return a child context for the stream."""
        return {
            "order_id": record["id"],
        }


class LineItemsStream(ZendeskSellStream):
    """Zendesk Sell line items stream class."""

    name = "line_items"
    parent_stream_type = OrdersStream
    path = "/orders/{order_id}/line_items"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]

    def get_records(self, context: Optional[dict] = None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        order_id = context.get("order_id") if context else None
        if order_id is None:
            self.logger.warning("Skipping LineItems: missing 'order_id' in context.")
            return

        # Use the standard request_records method but add order_id to each record
        for record in super().request_records(context):
            record["order_id"] = order_id
            yield record

    def get_url(self, context: Optional[dict]) -> str:
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
    """Zendesk Sell pipelines stream class."""

    name = "pipelines"
    path = "/pipelines"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class ProductsStream(ZendeskSellStream):
    """Zendesk Sell products stream class."""

    name = "products"
    path = "/products"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class StagesStream(ZendeskSellStream):
    """Zendesk Sell stages stream class."""

    name = "stages"
    path = "/stages"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class TagsStream(ZendeskSellStream):
    """Zendesk Sell tags stream class."""

    name = "tags"
    path = "/tags"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class TasksStream(ZendeskSellStream):
    """Zendesk Sell tasks stream class."""

    name = "tasks"
    path = "/tasks"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class TextMessagesStream(ZendeskSellStream):
    """Zendesk Sell text messages stream class."""

    name = "text_messages"
    path = "/text_messages"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class UsersStream(ZendeskSellStream):
    """Zendesk Sell users stream class."""

    name = "users"
    path = "/users"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class VisitOutcomesStream(ZendeskSellStream):
    """Zendesk Sell visit outcomes stream class."""

    name = "visit_outcomes"
    path = "/visit_outcomes"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


class VisitsStream(ZendeskSellStream):
    """Zendesk Sell visits stream class."""

    name = "visits"
    path = "/visits"
    records_jsonpath = "$.items[*].data"
    primary_keys: ClassVar[list[str]] = ["id"]


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