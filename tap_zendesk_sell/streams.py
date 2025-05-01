"""Zendesk Sell stream classes."""

from __future__ import annotations

from typing import ClassVar, Any, Dict, Optional, List, Mapping, TYPE_CHECKING, Iterable

import backoff
import requests

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

from tap_zendesk_sell import SCHEMAS_DIR
from tap_zendesk_sell.client import ZendeskSellStream
from singer_sdk import typing as th

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


class ContactsStream(ZendeskSellStream):
    """Zendesk Sell contacts stream class.

    https://developer.zendesk.com/api-reference/sales-crm/resources/contacts/
    """

    name = "contacts"
    path = "/contacts"
    records_jsonpath = "$.items[*].data"  # API returns items array with data objects
    primary_keys: ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"  # Use updated_at for incremental replication

    schema = PropertiesList(
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

    def get_child_context(self, record: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Return a context dictionary for child streams."""
        return {
            "contact_id": record["id"],
        }


class DealSourcesStream(ZendeskSellStream):
    """Zendesk Sell deal sources stream class."""

    name = "deal_sources"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "deal_sources.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.deal_sources.list(page=page, per_page=100)


class DealUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell deal unqualified reasons stream class."""

    name = "deal_unqualified_reasons"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "deal_unqualified_reasons.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.deal_unqualified_reasons.list(page=page, per_page=100)


class DealsStream(ZendeskSellStream):
    """Zendesk Sell deals stream class."""

    name = "deals"
    primary_keys: ClassVar[list[str]] = ["id"]

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

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.deals.list(page=page, per_page=100)

    def get_child_context(
        self, record: dict, context: Context | None  # noqa: ARG002
    ) -> dict:
        """Return a child context for the stream."""
        return {"deal_id": record["id"]}

    schema_filepath = SCHEMAS_DIR / "deals.json"


class AssociatedContacts(ZendeskSellStream):
    """Zendesk Sell associated contacts stream class."""

    name = "associated_contacts"
    parent_stream_type = DealsStream
    schema_filepath = SCHEMAS_DIR / "associated_contacts.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, deal_id: int, page: int) -> list:
        """List associated contacts for a specific deal."""
        return self.conn.associated_contacts.list(
            deal_id, page=page, per_page=100
        )

    def get_records(self, context: Context | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        deal_id = context.get("deal_id") if context else None
        if deal_id is None:
            self.logger.warning(
                "Skipping AssociatedContacts: missing 'deal_id' in context."
            )
            return

        while True:
            data = self.list_data(deal_id=deal_id, page=page)
            if not data:
                break
            for row in data:
                row["deal_id"] = deal_id
                yield row
            page += 1


class EventsStream(ZendeskSellStream):
    """Zendesk Sell events stream class."""

    name = "events"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "events.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.events.list(page=page, per_page=100)


class LeadSourcesStream(ZendeskSellStream):
    """Zendesk Sell lead sources stream class."""

    name = "lead_sources"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "lead_sources.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.lead_sources.list(page=page, per_page=100)


class LeadUnqualifiedReasonsStream(ZendeskSellStream):
    """Zendesk Sell lead unqualified reasons stream class."""

    name = "lead_unqualified_reasons"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "lead_unqualified_reasons.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.lead_unqualified_reasons.list(page=page, per_page=100)


class LeadsStream(ZendeskSellStream):
    """Zendesk Sell leads stream class."""

    name = "leads"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "leads.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.leads.list(page=page, per_page=100)


class LossReasonsStream(ZendeskSellStream):
    """Zendesk Sell loss reasons stream class."""

    name = "loss_reasons"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "loss_reasons.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.loss_reasons.list(page=page, per_page=100)


class NotesStream(ZendeskSellStream):
    """Zendesk Sell notes stream class."""

    name = "notes"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "notes.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.notes.list(page=page, per_page=100)


class OrdersStream(ZendeskSellStream):
    """Zendesk Sell orders stream class."""

    name = "orders"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "orders.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.orders.list(page=page, per_page=100)

    def get_child_context(self, record: dict, context: Optional[dict] = None) -> dict:
        """Return a child context for the stream."""
        return {
            "order_id": record["id"],
        }


class LineItemsStream(ZendeskSellStream):
    """Zendesk Sell line items stream class."""

    name = "line_items"
    parent_stream_type = OrdersStream
    schema_filepath = SCHEMAS_DIR / "line_items.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, order_id: int, page: int) -> list:
        """List line items for a specific order."""
        return self.conn.line_items.list(order_id, page=page, per_page=100)

    def get_records(self, context: Optional[dict] = None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        page = 1
        order_id = context.get("order_id") if context else None
        if order_id is None:
            self.logger.warning("Skipping LineItems: missing 'order_id' in context.")
            return

        while True:
            data = self.list_data(order_id=order_id, page=page)
            if not data:
                break
            for row in data:
                row["order_id"] = order_id
                yield row
            page += 1


class PipelinesStream(ZendeskSellStream):
    """Zendesk Sell pipelines stream class."""

    name = "pipelines"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "pipelines.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.pipelines.list(page=page, per_page=100)


class ProductsStream(ZendeskSellStream):
    """Zendesk Sell products stream class."""

    name = "products"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "products.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.products.list(page=page, per_page=100)


class StagesStream(ZendeskSellStream):
    """Zendesk Sell stages stream class."""

    name = "stages"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "stages.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.stages.list(page=page, per_page=100)


class TagsStream(ZendeskSellStream):
    """Zendesk Sell tags stream class."""

    name = "tags"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "tags.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.tags.list(page=page, per_page=100)


class TasksStream(ZendeskSellStream):
    """Zendesk Sell tasks stream class."""

    name = "tasks"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "tasks.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.tasks.list(page=page, per_page=100)


class TextMessagesStream(ZendeskSellStream):
    """Zendesk Sell text messages stream class."""

    name = "text_messages"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "text_messages.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.text_messages.list(page=page, per_page=100)


class UsersStream(ZendeskSellStream):
    """Zendesk Sell users stream class."""

    name = "users"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "users.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.users.list(page=page, per_page=100)


class VisitOutcomesStream(ZendeskSellStream):
    """Zendesk Sell visit outcomes stream class."""

    name = "visit_outcomes"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "visit_outcomes.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.visit_outcomes.list(page=page, per_page=100)


class VisitsStream(ZendeskSellStream):
    """Zendesk Sell visits stream class."""

    name = "visits"
    primary_keys: ClassVar[list[str]] = ["id"]
    schema_filepath = SCHEMAS_DIR / "visits.json"

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_value=10,
    )
    def list_data(self, page: int) -> list:
        """List data from the API."""
        return self.conn.visits.list(page=page, per_page=100)


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