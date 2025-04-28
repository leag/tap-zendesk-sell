"""Zendesk Sell Base Stream class."""

from __future__ import annotations

import typing as t

import basecrm
from singer_sdk.streams import Stream
from singer_sdk.tap_base import Tap

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class ZendeskSellStream(Stream):
    """Zendesk Sell sync stream class."""

    address_properties = {
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

    custom_field_type: dict[str, dict] = {
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
    resource_types = {
        "deal",
        "contact",
        "lead",
        "prospect_and_customer",
    }

    _conn: basecrm.Client | None = None  # Cache for the connection

    @property
    def conn(self) -> basecrm.Client:
        """Get or initialize the API client connection."""
        if self._conn is None:
            access_token = self.config.get("access_token")
            if not access_token:
                # Tap-level validation should catch this, but raise if accessed before config
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
            # Use f-string correctly
            raise ValueError(f"{resource_type_set} is not a valid resource type set")

        custom_fields_properties = {}
        for resource_type in resource_type_set:
            # Use the conn property here - it handles initialization
            _, _, data = self.conn.http_client.get(f"/{resource_type}/custom_fields")
            for custom_field in data:
                field_name = custom_field["name"]
                field_type = custom_field["type"]
                type_dict = self.custom_field_type[field_type]
                if field_name not in custom_fields_properties:
                    custom_fields_properties[field_name] = type_dict
                elif custom_fields_properties[field_name] != type_dict:
                    # Accessing nested type info might need adjustment if structure varies
                    # Assuming multi_select_list is the main conflict source
                    other_type_desc = "unknown"
                    if "items" in type_dict and "type" in type_dict["items"]:
                        other_type_desc = str(type_dict["items"]["type"])
                    elif "type" in type_dict:
                        other_type_desc = str(type_dict["type"])

                    # Use field_name and field_type from variables
                    msg = (
                        f"Custom field name conflict: {field_name}, "
                        f"Type: {field_type}, "
                        f"Conflicts with existing type: {other_type_desc}"
                    )
                    raise ValueError(msg)
        return custom_fields_properties

    def __init__(self, tap: Tap):
        """Initialize the stream."""
        super().__init__(tap)

    def get_records(
        self,
        context: Context | None,
    ) -> t.Iterable[dict]:
        """Return a generator of record-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.

        Args:
            context: Stream partition or context dictionary.

        Raises:
            NotImplementedError: If the implementation is TODO
        """
        errmsg = "The method is not yet implemented (TODO)"
        raise NotImplementedError(errmsg)
