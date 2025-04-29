"""Zendesk Sell Base Stream class."""

from __future__ import annotations

import typing as t

import basecrm
from singer_sdk.streams import Stream

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.helpers.types import Context


class ZendeskSellStream(Stream):
    """Zendesk Sell sync stream class."""

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

    _conn: basecrm.Client | None = None

    @property
    def conn(self) -> basecrm.Client:
        """Get or initialize the API client connection."""
        if self._conn is None:
            access_token = self.config.get("access_token")
            if not access_token:
                msg = "Access token is required but not found in config."
                raise ValueError(msg)
            self._conn = basecrm.Client(access_token=access_token)
        return self._conn

    def _update_schema(self, resource_type_set: set | None = None) -> dict:
        """Update the schema for this stream with custom fields."""
        if resource_type_set is None:
            resource_type_set = {
                "deal",
                "contact",
                "lead",
                "prospect_and_customer",
            }
        if not resource_type_set.issubset(self.resource_types):
            msg = f"{resource_type_set} is not a valid resource type set"
            raise ValueError(msg)

        custom_fields_properties = {}
        for resource_type in resource_type_set:
            _, _, data = self.conn.http_client.get(f"/{resource_type}/custom_fields")
            for custom_field in data:
                field_name = custom_field["name"]
                field_type = custom_field["type"]
                type_dict = self.custom_field_type[field_type]
                if field_name not in custom_fields_properties:
                    custom_fields_properties[field_name] = type_dict
                elif custom_fields_properties[field_name] != type_dict:
                    other_type_desc = "unknown"
                    if "items" in type_dict and "type" in type_dict["items"]:
                        other_type_desc = str(type_dict["items"]["type"])
                    elif "type" in type_dict:
                        other_type_desc = str(type_dict["type"])

                    msg = (
                        f"Custom field name conflict: {field_name}, "
                        f"Type: {field_type}, "
                        f"Conflicts with existing type: {other_type_desc}"
                    )
                    raise ValueError(msg)
        return custom_fields_properties

    def list_data(self, page: int) -> list:
        """List data from the API.

        This method should be overridden in subclasses that support simple pagination.
        It is expected to return a list of dictionaries representing the data.

        Args:
            page (int): The page number to retrieve.
            per_page (int): The number of records to return per page.
            sort_by (str): The field to sort by.
        """
        errmsg = f"list_data is not implemented for stream '{self.name}'"
        raise NotImplementedError(errmsg)

    def get_records(self, _context: Context | None) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects.

        This default implementation handles simple pagination using the list_data method
        Streams with different pagination or fetching logic should override this.
        """
        page = 1
        while True:
            try:
                data = self.list_data(page=page)
            except NotImplementedError:
                self.logger.exception(
                    "Stream '%s' does not implement list_data method required for "
                    "default get_records pagination.",
                    self.name,
                )
                raise
            except Exception:
                self.logger.exception(
                    "Error fetching data for stream '%s' on page %s",
                    self.name,
                    page,
                )
                break

            if not data:
                break
            yield from data
            page += 1
