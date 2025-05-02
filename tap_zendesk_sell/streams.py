"""Zendesk Sell stream classes."""

from __future__ import annotations

from functools import cached_property
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

import requests

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.helpers.types import Context
from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.zendesk_types import (
    AddressType,
    ArrayType,
    BooleanType,
    DateTimeType,
    DateType,
    IntegerType,
    NumberType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)


def safe_float(value: str | None) -> float | None:
    """Safely convert a value to float, returning None on error."""
    if value is None:
        return None
    try:
        return float(value)
    except TypeError:
        return None


class AccountsStream(ZendeskSellStream):
    """Zendesk Sell accounts stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/account/
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
            Property("is_organization", BooleanType),
            Property("contact_id", IntegerType),
            Property("parent_organization_id", IntegerType),
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
            Property("tags", ArrayType(StringType, nullable=True)),
            Property("custom_fields", ObjectType()),
            Property("created_at", DateTimeType),
            Property("updated_at", DateTimeType),
        ).to_dict()

        # Add custom fields
        custom_fields_properties = self._fetch_custom_field_schema({"contact"})
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
        Property("creator_id", IntegerType),
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
            Property("dropbox_email", StringType),
            Property("contact_id", IntegerType),
            Property("organization_id", IntegerType),
            Property("estimated_close_date", StringType),
            Property("customized_win_likelihood", IntegerType),
            Property("tags", ArrayType(StringType, nullable=True)),
            Property("created_at", DateTimeType),
            Property("updated_at", DateTimeType),
            Property("added_at", DateTimeType),
        ).to_dict()

        # Add custom fields
        custom_fields_properties = self._fetch_custom_field_schema({"deal"})
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

    def post_process(self, row: dict, context: Context | None) -> dict:  # noqa: ARG002
        """Post-process the record before yielding it."""
        row["value"] = safe_float(row.get("value"))
        return row


class AssociatedContacts(ZendeskSellStream):
    """Zendesk Sell associated contacts stream class."""

    name = "associated_contacts"
    parent_stream_type = DealsStream
    path = "/deals/{deal_id}/associated_contacts"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("contact_id", IntegerType),
        Property("role", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()

    def post_process(self, row: dict, context: Context | None) -> dict:
        """Post-process the record before yielding it."""
        row["deal_id"] = context["deal_id"]
        return row


class EventsStream(ZendeskSellStream):
    """Zendesk Sell events stream class.

    Events are emitted when resources change in the system.
    https://developer.zendesk.com/api-reference/sales-crm/sync/introduction/
    https://developer.zendesk.com/api-reference/sales-crm/sync/protocol/
    https://developer.zendesk.com/api-reference/sales-crm/sync/requests/
    https://developer.zendesk.com/api-reference/sales-crm/sync/reference/

    meta.type:
    - account
    - contact
    - deal
    - lead
    - loss_reason
    - note
    - pipeline
    - source
    - tag
    - task
    - user

    meta.sync.event_type:
    - create
    - update
    - delete
    """

    name = "events"
    path = "/sync"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

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
        ),
        Property(
            "data",
            ObjectType(
                Property("id", IntegerType),
                Property("resource_type", StringType),
                Property("resource_id", IntegerType),
                Property("type", StringType),
                Property("creator_id", IntegerType),
                Property("created_at", StringType),
                Property("name", StringType),
                Property("value", StringType),
                Property("currency", StringType),
                Property("owner_id", IntegerType),
                Property("email", StringType),
                Property("phone", StringType),
                Property("address", AddressType),
                Property("tags", ArrayType(StringType, nullable=True)),
                Property("updated_at", StringType),
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
            Property("tags", ArrayType(StringType, nullable=True)),
            Property("unqualified_reason_id", IntegerType),
            Property("created_at", DateTimeType),
            Property("updated_at", DateTimeType),
        ).to_dict()

        # Add custom fields
        custom_fields_properties = self._fetch_custom_field_schema({"lead"})
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
        Property("tags", ArrayType(StringType, nullable=True)),
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

    https://developer.zendesk.com/api-reference/sales-crm/resources/line-items/
    """

    name = "line_items"
    parent_stream_type = OrdersStream
    path = "/orders/{order_id}/line_items"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("id", IntegerType),
        Property("order_id", IntegerType),
        Property("product_id", IntegerType),
        Property("value", NumberType),
        Property("variation", NumberType),
        Property("currency", StringType),
        Property("quantity", IntegerType),
        Property("price", NumberType),
        Property("name", StringType),
        Property("sku", StringType),
        Property("description", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()

    def post_process(self, row: dict, context: dict | None) -> dict:
        """Post-process the record before yielding it."""
        row["order_id"] = context["order_id"]
        row["value"] = safe_float(row.get("value"))
        row["price"] = safe_float(row.get("price"))
        row["quantity"] = safe_float(row.get("quantity"))
        row["variation"] = safe_float(row.get("variation"))
        return row


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
        Property(
            "prices",
            ArrayType(
                ObjectType(
                    Property("amount", NumberType),
                    Property("currency", StringType),
                ),
                nullable=True,
            ),
        ),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
    ).to_dict()

    def post_process(self, row: dict, context: dict | None) -> dict:  # noqa: ARG002
        """Post-process the record before yielding it."""
        row["cost"] = safe_float(row.get("cost"))
        row["max_discount"] = safe_float(row.get("max_discount"))
        row["max_markup"] = safe_float(row.get("max_markup"))

        prices = row.get("prices", [])
        if isinstance(prices, list):
            for price in prices:
                if isinstance(price, dict):
                    price["amount"] = safe_float(price.get("amount"))

        return row


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
        Property("resource_type", StringType),
        Property("resource_id", IntegerType),
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

    https://developer.zendesk.com/api-reference/sales-crm/resources/text-messages/
    """

    name = "text_messages"
    path = "/text_messages"
    records_jsonpath = "$.items[*].data"
    primary_keys = ("id",)

    schema = PropertiesList(
        Property("associated_deal_ids", ArrayType(IntegerType, nullable=True)),
        Property("content", StringType),
        Property("created_at", DateTimeType),
        Property("id", IntegerType),
        Property("incoming", BooleanType),
        Property("resource_id", IntegerType),
        Property("resource_type", StringType),
        Property("resource_phone_number", StringType),
        Property("sent_at", DateTimeType),
        Property("user_id", IntegerType),
        Property("user_phone_number", StringType),
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
        Property("status", StringType),
        Property("invited", BooleanType),
        Property("confirmed", BooleanType),
        Property("phone_number", StringType),
        Property("role", StringType),
        Property(
            "roles",
            ArrayType(
                ObjectType(
                    Property("id", IntegerType),
                    Property("name", StringType),
                ),
            ),
        ),
        Property("team_name", StringType),
        Property(
            "group",
            ObjectType(
                Property("id", IntegerType),
                Property("name", StringType),
            ),
        ),
        Property("reports_to", IntegerType),
        Property("timezone", StringType),
        Property("created_at", DateTimeType),
        Property("updated_at", DateTimeType),
        Property("deleted_at", DateTimeType),
        Property("zendesk_user_id", StringType),
        Property("identity_type", StringType),
        Property("system_tags", ArrayType(StringType)),
        Property("detached", BooleanType),
        Property("sell_login_disabled", BooleanType),
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
