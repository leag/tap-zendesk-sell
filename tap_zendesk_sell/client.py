"""Zendesk Sell Base Stream class."""

from __future__ import annotations

import typing as t
from http import HTTPStatus

import requests
import requests.auth
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream

if t.TYPE_CHECKING:
    from collections.abc import Iterable


from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath


class ZendeskSellPaginator(BaseAPIPaginator):
    """Zendesk Sell API paginator class."""

    def __init__(
        self,
        start_page: int = 1,
        page_size: int = 100,
    ) -> None:
        """Initialize the paginator.

        Args:
            start_page: The initial page number.
            page_size: The number of records per page.
        """
        self._current_page = start_page
        self._page_size = page_size
        self._next_page_url = None
        self._finished = False

    def has_more(self) -> bool:
        """Check if there are more pages to process.

        Returns:
            Boolean flag used to indicate if there are more pages to process.
        """
        return not self._finished

    def get_next(self, response: requests.Response) -> int:
        """Get the next page number.

        Args:
            response: API response object.

        Returns:
            The next page number.
        """
        if response.status_code != HTTPStatus.OK:
            self._finished = True
            return self._current_page

        json_data = response.json()
        json_data = response.json()
        meta = json_data.get("meta", {})
        links = meta.get("links", {})

        # Check if there's a next page link
        next_page_url = links.get("next_page")

        if not next_page_url:
            self._finished = True
            return self._current_page

        # Store the next page URL for later use
        self._next_page_url = next_page_url

        # Increment the current page
        self._current_page += 1
        return self._current_page

    @property
    def next_page_url(self) -> str | None:
        """Get the next page URL.

        Returns:
            URL for the next page or None if no more pages.
        """
        return self._next_page_url

    @property
    def page_size(self) -> int | None:
        """Get the page size.

        Returns:
            The number of records per page.
        """
        return self._page_size


class ZendeskSellStream(RESTStream):
    """Zendesk Sell sync stream class."""

    url_base = "https://api.getbase.com/v2"
    records_jsonpath = "$.items[*].data"  # Default JSON path for most resources

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Initialize the stream.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self._paginator = None
        super().__init__(*args, **kwargs)

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

    def get_new_paginator(self) -> ZendeskSellPaginator:
        """Create a new paginator instance.

        Returns:
            A paginator instance.
        """
        if self._paginator is None:
            self._paginator = ZendeskSellPaginator(
                start_page=1,
                page_size=self.config.get("page_size", 100),  # Default to max page size
            )
        return self._paginator

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: int | None,
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: Stream sync context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL parameter values.
        """
        params = {}

        # If we have a specific next_page_url from the paginator, use that instead
        paginator = self.get_new_paginator()
        if paginator.next_page_url and next_page_token:
            # In this case, we'll use the next_page_url directly
            # in the request_records method
            return params

        # Add pagination parameters
        if next_page_token:
            params["page"] = next_page_token
        else:
            params["page"] = 1

        # Add page size
        params["per_page"] = self.config.get("page_size", 100)

        # Add any stream-specific parameters
        if self.replication_key and self.get_starting_replication_key_value(context):
            start_date = self.get_starting_replication_key_value(context)
            if start_date:
                params[f"{self.replication_key}>"] = start_date

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of records.

        Args:
            response: The HTTP response object.

        Yields:
            Each record from the source.
        """
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def get_next_page_token(
        self, response: requests.Response, previous_token: int | None  # noqa: ARG002
    ) -> int | None:
        """Return a token for identifying next page or None if no more pages.

        Args:
            response: The HTTP response object.
            previous_token: The previous page token.

        Returns:
            The next page token or None if no more pages.
        """
        # Use our paginator to determine the next page
        paginator = self.get_new_paginator()
        next_page = paginator.get_next(response)

        if paginator.has_more():
            return next_page

        return None

    def request_records(self, context: dict | None) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.

        If pagination is detected, pages will be recursively queried until
        no more pages remain.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            An item for every record in the response.
        """
        paginator = self.get_new_paginator()
        decorated_request = self.request_decorator(self._request)

        # Initialize next_page_token to None before first request
        next_page_token = None

        while True:
            # If we have a next_page_url from previous response, use that directly
            if paginator.next_page_url and next_page_token:
                prepared_request = self.prepare_request(
                    context,
                    next_page_token=next_page_token,
                )
                # Override the URL with the next_page_url
                prepared_request.url = paginator.next_page_url
            else:
                prepared_request = self.prepare_request(
                    context,
                    next_page_token=next_page_token,
                )

            resp = decorated_request(prepared_request, context)
            yield from self.parse_response(resp)

            # Get token for next page
            next_page_token = self.get_next_page_token(resp, next_page_token)

            # Exit loop if no more pages
            if not next_page_token:
                break

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
            self.logger.exception(
                "Error fetching custom fields for %s", resource_type
            )
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
                    if ("items" in existing_type_info
                            and "type" in existing_type_info["items"]):
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
