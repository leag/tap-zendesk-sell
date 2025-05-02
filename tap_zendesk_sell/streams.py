"""Zendesk Sell stream classes."""

from __future__ import annotations

from functools import cached_property
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

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
    Property("line1", StringType),
    Property("city", StringType),
    Property("postal_code", StringType),
    Property("state", StringType),
    Property("country", StringType),
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
    primary_keys = ("id",)
    records_jsonpath = "data.[*]"
    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("currency", StringType),
        Property("time_format", StringType),
        Property("timezone", StringType),
        Property("phone", StringType),
        Property("subdomain", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
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
            Property("id", IntegerType),
            Property("creator_id", IntegerType),
            Property("owner_id", IntegerType),
            Property("contact_id", IntegerType),
            Property("parent_organization_id", IntegerType),
            Property("is_organization", BooleanType),
            Property("name", StringType),
            Property("first_name", StringType),
            Property("last_name", StringType),
            Property("customer_status", StringType),
            Property("prospect_status", StringType),
            Property("title", StringType),
            Property("description", StringType),
            Property("industry", StringType),
            Property("website", StringType),
            Property("email", StringType),
            Property("phone", StringType),
            Property("mobile", StringType),
            Property("fax", StringType),
            Property("twitter", StringType),
            Property("facebook", StringType),
            Property("linkedin", StringType),
            Property("skype", StringType),
            Property("address", AddressType),
            Property("billing_address", AddressType),
            Property("shipping_address", AddressType),
            Property("tags", ArrayType(StringType)),
            Property("custom_fields", ObjectType()),
            Property("created_at", DateTimeType),
            Property("updated_at", DateTimeType),
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
        Property("id", IntegerType),
        Property("creator_id",IntegerType),
        Property("name", StringType),
        Property("resource_type", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class DealUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell deal unqualified reasons stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/deal-unqualified-reasons/
    """

    name = "deal_unqualified_reasons"
    path = "/deal_unqualified_reasons"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("creator_id", IntegerType),
        Property("name", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class DealsStream(ZendeskSellStream):
    """Zendesk Sell deals stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/deals/
    """

    name = "deals"
    path = "/deals"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)
    replication_key = "updated_at"

    @cached_property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for deals."""
        base_schema = PropertiesList(
            Property("id", IntegerType),
            Property("creator_id", IntegerType),
            Property("owner_id", IntegerType),
            Property("name", StringType),
            Property("value", NumberType),
            Property("currency", StringType),
            Property("hot", BooleanType),
            Property("stage_id", IntegerType),
            Property("last_stage_change_at", DateTimeType),
            Property("last_stage_change_by_id", IntegerType),
            Property("last_activity_at", DateTimeType),
            Property("source_id", IntegerType),
            Property("loss_reason_id", IntegerType),
            Property("unqualified_reason_id", IntegerType),
            Property("contact_id", IntegerType),
            Property("organization_id", IntegerType),
            Property("estimated_close_date", StringType),
            Property("customized_win_likelihood", IntegerType),
            Property("dropbox_email", StringType),
            Property("tags", ArrayType(StringType) ),
            Property("associated_contacts", ObjectType()),
            Property("created_at", DateTimeType),
            Property("updated_at", DateTimeType),
            Property("added_at", DateTimeType),
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
        self,
        record: dict,
        context: Context | None,  # noqa: ARG002
    ) -> dict:
        """Return a child context for the stream."""
        return {"deal_id": record["id"]}


class AssociatedContacts(ContactsStream):
    """Zendesk Sell associated contacts stream class."""

    name = "associated_contacts"
    parent_stream_type = DealsStream
    path = "/deals/{deal_id}/associated_contacts"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

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
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("meta", ObjectType( Property("version", IntegerType),
                Property("type", StringType),
                Property("sync", ObjectType( Property("revision", IntegerType),
                        Property("event_type", StringType),
                        Property("ack_key", StringType),
                    ),
                ),
            ),
        ),
        Property("data", ObjectType( Property("id", IntegerType),
                Property("resource_type", StringType),
                Property("resource_id", IntegerType),
                Property("type", StringType),
                Property("creator_id", IntegerType),
                Property("created_at", StringType),
                # The following fields depend on the resource_type and may be present
                Property("name", StringType),
                Property("value", StringType),
                Property("currency", StringType),
                Property("owner_id", IntegerType),
                Property("email", StringType),
                Property("phone", StringType),
                Property("address", AddressType),
                Property("tags", ArrayType(StringType)),
                Property("updated_at", StringType),
                # Many more fields may be present depending on the event type
            ),
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
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("creator_id", IntegerType),
        Property("name", StringType),
        Property("resource_type", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class LeadUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell lead unqualified reasons stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/lead-unqualified-reasons/
    """

    name = "lead_unqualified_reasons"
    path = "/lead_unqualified_reasons"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("creator_id", IntegerType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/leads/
    """

    name = "leads"
    path = "/leads"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)
    replication_key = "updated_at"

    @cached_property
    def schema(self) -> dict:
        """Dynamically discover and apply schema properties for leads."""
        base_schema = PropertiesList(
            Property("id", IntegerType),
            Property("creator_id", IntegerType),
            Property("owner_id", IntegerType),
            Property("first_name", StringType),
            Property("last_name", StringType),
            Property("organization_name", StringType),
            Property("status", StringType),
            Property("source_id", IntegerType),
            Property("title", StringType),
            Property("description", StringType),
            Property("industry", StringType),
            Property("website", StringType),
            Property("email", StringType),
            Property("phone", StringType),
            Property("mobile", StringType),
            Property("fax", StringType),
            Property("twitter", StringType),
            Property("facebook", StringType),
            Property("linkedin", StringType),
            Property("skype", StringType),
            Property("address", AddressType),
            Property("tags", ArrayType(StringType) ),
            Property("unqualified_reason_id", IntegerType),
            Property("created_at", DateTimeType),
            Property("updated_at", DateTimeType),
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
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("creator_id", IntegerType),
        Property("name", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class NotesStream(ZendeskSellStream):
    """Zendesk Sell notes stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/notes/
    """

    name = "notes"
    path = "/notes"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("creator_id", IntegerType),
        Property("resource_type", StringType),
        Property("resource_id", IntegerType),
        Property("content", StringType),
        Property("is_important", BooleanType),
        Property("tags", ArrayType(StringType)),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
        Property("type", StringType),
    ).to_dict()


class OrdersStream(ZendeskSellStream):
    """Zendesk Sell orders stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/orders/
    """

    name = "orders"
    path = "/orders"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)
    replication_key = "updated_at"

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("deal_id", IntegerType),
        Property("discount", IntegerType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()

    def get_child_context(
        self,
        record: dict,
        context: dict | None = None,  # noqa: ARG002
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
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("order_id", IntegerType),
        Property("line_item_id", IntegerType),
        Property("name", StringType),
        Property("sku", StringType),
        Property("description", StringType),
        Property("value", NumberType),
        Property("variation", NumberType),
        Property("price", NumberType),
        Property("currency", StringType),
        Property("quantity", IntegerType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
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
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class ProductsStream(ZendeskSellStream):
    """Zendesk Sell products stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/products/
    """

    name = "products"
    path = "/products"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("creator_id", IntegerType),
        Property("name", StringType),
        Property("sku", StringType),
        Property("description", StringType),
        Property("active", BooleanType),
        Property("max_discount", NumberType),
        Property("max_markup", NumberType),
        Property("cost", NumberType),
        Property("cost_currency", StringType),
        Property("prices", ArrayType( ObjectType(
                    Property("amount", NumberType),
                    Property("currency", StringType),
                )
            ),
        ),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class StagesStream(ZendeskSellStream):
    """Zendesk Sell stages stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/stages/
    """

    name = "stages"
    path = "/stages"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("category", StringType),
        Property("likelihood", IntegerType),
        Property("active", BooleanType),
        Property("pipeline_id", IntegerType),
        Property("position", IntegerType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class TagsStream(ZendeskSellStream):
    """Zendesk Sell tags stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/tags/
    """

    name = "tags"
    path = "/tags"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("resource_type", StringType),
        Property("creator_id", IntegerType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class TasksStream(ZendeskSellStream):
    """Zendesk Sell tasks stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/tasks/
    """

    name = "tasks"
    path = "/tasks"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("creator_id", IntegerType),
        Property("owner_id", IntegerType),
        Property("resource_id", IntegerType),
        Property("resource_type", StringType),
        Property("completed", BooleanType),
        Property("completed_at", DateTimeType),
        Property("due_date", DateTimeType),
        Property("overdue", BooleanType),
        Property("remind_at", DateTimeType),
        Property("content", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class TextMessagesStream(ZendeskSellStream):
    """Zendesk Sell text messages stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/text_messages/
    """

    name = "text_messages"
    path = "/text_messages"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("creator_id", IntegerType),
        Property("resource_id", IntegerType),
        Property("resource_type", StringType),
        Property("phone_number", StringType),
        Property("content", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class UsersStream(ZendeskSellStream):
    """Zendesk Sell users stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/users/
    """

    name = "users"
    path = "/users"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("email", StringType),
        Property("role", StringType),
        Property("status", StringType),
        Property("reports_to", IntegerType),
        Property("group", ObjectType( Property("id", IntegerType),
                Property("name", StringType),
            ),
        ),
        Property("team_name", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class VisitOutcomesStream(ZendeskSellStream):
    """Zendesk Sell visit outcomes stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/visit-outcomes/
    """

    name = "visit_outcomes"
    path = "/visit_outcomes"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("name", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()


class VisitsStream(ZendeskSellStream):
    """Zendesk Sell visits stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/visits/
    """

    name = "visits"
    path = "/visits"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("creator_id", IntegerType),
        Property("resource_type", StringType),
        Property("resource_id", IntegerType),
        Property("user_id", IntegerType),
        Property("outcome_id", IntegerType),
        Property("summary", StringType),
        Property("date", DateType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
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
