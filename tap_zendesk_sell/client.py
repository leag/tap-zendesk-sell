"""Zendesk Sell Base Stream class."""

from __future__ import annotations

import typing as t

import requests
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.streams import RESTStream

from tap_zendesk_sell.zendesk_types import (
    AddressType,
    ArrayType,
    BooleanType,
    DateTimeType,
    DateType,
    StringType,
)

ResourceTypes = {
    "deal",
    "contact",
    "lead",
    "prospect_and_customer",
}


CustomFieldTypes = {
    "address": AddressType,
    "bool": BooleanType,
    "boolean": BooleanType,
    "date": DateType,
    "datetime": DateTimeType,
    "email": StringType,
    "list": StringType,
    "multi_select_list": ArrayType(StringType),
    "number": StringType,
    "phone": StringType,
    "string": StringType,
    "text": StringType,
    "url": StringType,
}


class ZendeskSellStream(RESTStream):
    """Zendesk Sell sync stream class."""

    url_base = "https://api.getbase.com/v2"
    records_jsonpath = "$.items[*].data"  # Default JSON path for most resources

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("access_token", ""),
        )

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: int | None,
    ) -> dict[str, t.Any]:
        """Return URL params for pagination."""
        page = next_page_token or 1
        return {
            "page": page,
            "per_page": self.config.get("page_size", 100),
        }

    def get_next_page_token(
        self, response: requests.Response, previous_token: int | None
    ) -> int | None:
        """Return next page token or None if no more pages."""
        links = response.json().get("meta", {}).get("links", {})
        if links.get("next_page"):
            return (previous_token or 1) + 1
        return None

    def _fetch_and_process_custom_fields(
        self,
        resource_type: str,
        custom_fields_properties: dict,
    ) -> None:
        """Fetch and process custom fields for a resource type.

        https://developer.zendesk.com/api-reference/sales-crm/resources/custom-fields/
        """
        path = "/{resource_type}/custom_fields"

        try:
            request = self.build_prepared_request(
                method="GET",
                url=self.url_base + path.format(resource_type=resource_type),
            )
            response = self.requests_session.send(request)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            self.logger.exception("Error fetching custom fields for %s", resource_type)
            return

        data = response.json().get("items", [])

        for custom_field in data:
            field_data = custom_field.get("data", {})
            field_name = field_data.get("name")
            field_type = field_data.get("type")

            if not field_name or not field_type:
                self.logger.warning(
                    "Skipping custom field with missing name or type: %s", custom_field
                )
                continue

            if field_type in CustomFieldTypes:
                # Convert the type instance to a schema dict to avoid AttributeError
                type_instance = CustomFieldTypes[field_type]
                if hasattr(type_instance, "to_dict"):
                    type_dict = type_instance.to_dict()
                else:
                    # For types like ArrayType that might not have to_dict
                    type_dict = {"type": "string", "nullable": True}

                if field_name not in custom_fields_properties:
                    custom_fields_properties[field_name] = type_dict
                elif custom_fields_properties[field_name] != type_dict:
                    # Determine existing type description for logging
                    existing_type_info = custom_fields_properties[field_name]
                    existing_type_desc = "unknown"
                    if (
                        "items" in existing_type_info
                        and "type" in existing_type_info["items"]
                    ):
                        existing_type_desc = str(existing_type_info["items"]["type"])
                    elif "type" in existing_type_info:
                        existing_type_desc = str(existing_type_info["type"])

                    self.logger.warning(
                        "Custom field name conflict: '%s'. Type '%s' for resource '%s' "
                        "conflicts with existing type definition '%s'. "
                        "Keeping the existing type definition.",
                        field_name,
                        field_type,
                        resource_type,
                        existing_type_desc,
                    )
            else:
                self.logger.warning(
                    (
                        "Unsupported custom field type '%s' for field '%s' "
                        "in resource '%s'"
                    ),
                    field_type,
                    field_name,
                    resource_type,
                )

    def _fetch_custom_field_schema(self, resource_type_set: set | None = None) -> dict:
        """Update the schema for this stream with custom fields.

        Args:
            resource_type_set: Set of resource types to get custom fields for.
                               defaults to all resource types.

        Returns:
            Dictionary of custom field properties.
        """
        if resource_type_set is None:
            resource_type_set = ResourceTypes  # Default to all resource types

        if not resource_type_set.issubset(ResourceTypes):
            invalid_types = resource_type_set - ResourceTypes
            msg = (
                f"Invalid resource type(s) provided: {invalid_types}. "
                f"Valid types are: {ResourceTypes}"
            )
            raise ValueError(msg)

        custom_fields_properties: dict[str, dict] = {}
        for resource_type in resource_type_set:
            self._fetch_and_process_custom_fields(
                resource_type, custom_fields_properties
            )

        return custom_fields_properties
