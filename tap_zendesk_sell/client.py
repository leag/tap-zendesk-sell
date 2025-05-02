"""Zendesk Sell Base Stream class."""

from __future__ import annotations

import typing as t

import requests
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.streams import RESTStream


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

    address_properties: t.ClassVar[dict[str, dict]] = {
        "line1": {
            "type": ["string", "null"],
            "description": "Line 1 of the address.",
        },
        "city": {"type": ["string", "null"], "description": "City name."},
        "postal_code": {
            "type": ["string", "null"],
            "description": "Zip code or equivalent.",
        },
        "state": {"type": ["string", "null"], "description": "State name."},
        "country": {
            "type": ["string", "null"],
            "description": "Country name.",
        },
    }

    custom_field_type: t.ClassVar[dict[str, dict]] = {
        "address": {
            "type": ["object", "null"],
            "properties": address_properties,
        },
        "bool": {"type": ["boolean", "null"]},
        "boolean": {"type": ["boolean", "null"]},
        "date": {"type": ["string", "null"]},
        "datetime": {"type": ["string", "null"], "format": "date-time"},
        "email": {"type": ["string", "null"]},
        "list": {"type": ["string", "null"]},
        "multi_select_list": {
            "type": ["array", "null"],
            "items": {"type": ["string"]},
        },
        "number": {"type": ["string", "null"]},
        "phone": {"type": ["string", "null"]},
        "string": {"type": ["string", "null"]},
        "text": {"type": ["string", "null"]},
        "url": {"type": ["string", "null"]},
    }
    resource_types: t.ClassVar[set[str]] = {
        "deal",
        "contact",
        "lead",
        "prospect_and_customer",
    }

    def _process_single_resource_type_fields(
        self,
        resource_type: str,
        access_token: str,
        custom_fields_properties: dict,
    ) -> None:
        """Fetch and process custom fields for a single resource type."""
        url = f"{self.url_base}/{resource_type}/custom_fields"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            # Assuming self.request_timeout exists from RESTStream
            timeout = getattr(self, "request_timeout", 300)
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            self.logger.exception("Error fetching custom fields for %s", resource_type)
            # Log and continue to avoid breaking the whole sync for one error
            return

        data = response.json().get("items", [])  # Use .get for safety

        for custom_field in data:
            field_data = custom_field.get("data", {})  # Use .get
            field_name = field_data.get("name")
            field_type = field_data.get("type")

            if not field_name or not field_type:
                self.logger.warning(
                    "Skipping custom field with missing name or type: %s", custom_field
                )
                continue  # Skip malformed fields

            if field_type in self.custom_field_type:
                type_dict = self.custom_field_type[field_type]
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

                    # Log the conflict instead of raising an error
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

    def _update_schema(self, resource_type_set: set | None = None) -> dict:
        """Update the schema for this stream with custom fields.

        Args:
            resource_type_set: Set of resource types to get custom fields for.

        Returns:
            Dictionary of custom field properties.
        """
        if resource_type_set is None:
            # Use the class variable directly for the default set
            resource_type_set = self.resource_types

        if not resource_type_set.issubset(self.resource_types):
            invalid_types = resource_type_set - self.resource_types
            msg = (
                f"Invalid resource type(s) provided: {invalid_types}. "
                f"Valid types are: {self.resource_types}"
            )
            raise ValueError(msg)

        access_token = self.config.get("access_token")
        if not access_token:
            msg = "Access token is required but not found in config."
            raise ValueError(msg)

        custom_fields_properties: dict[str, dict] = {}
        for resource_type in resource_type_set:
            self._process_single_resource_type_fields(
                resource_type, access_token, custom_fields_properties
            )

        return custom_fields_properties
