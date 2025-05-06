"""Zendesk Sell Base Stream class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import basecrm
from singer_sdk.streams import Stream

if TYPE_CHECKING:
    from collections.abc import Iterable

    from singer_sdk.tap_base import Tap

custom_field_type_map = {
    "address": {
        "type": ["object", "null"],
        "properties": {
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
        },
    },
    "bool": {"type": ["boolean", "null"]},
    "boolean": {"type": ["boolean", "null"]},
    "date": {"type": ["string", "null"], "format": "date"},
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
custom_field_resource_types = {
    "deal",
    "contact",
    "lead",
    "prospect_and_customer",
}


class ZendeskSellStream(Stream):
    """Zendesk Sell sync stream class."""

    def _build_custom_field_schema(self, resource_types: set | None = None) -> dict:
        """Update the schema for this stream with custom fields."""
        if resource_types is None:
            resource_types = custom_field_resource_types
        if not resource_types.issubset(custom_field_resource_types):
            msg = f"{resource_types} is not a valid resource type set"
            raise ValueError(msg)

        custom_fields_properties = {}
        for resource_type in resource_types:
            _, _, data = self.conn.http_client.get(f"/{resource_type}/custom_fields")
            for custom_field in data:
                type_dict = custom_field_type_map[custom_field["type"]]
                if custom_field["name"] not in custom_fields_properties:
                    custom_fields_properties[custom_field["name"]] = type_dict
                elif custom_fields_properties[custom_field["name"]] != type_dict:
                    raise ValueError(
                        " ".join(
                            [
                                f"Custom field name conflict: {custom_field.name},",
                                f"Type: {custom_field.type},",
                                f"Other Type: {type_dict['items']['type'][0]}",
                            ]
                        )
                    )
        return custom_fields_properties

    @property
    def conn(self) -> basecrm.Client:
        """Return the connection to the Zendesk Sell API."""
        if not hasattr(self, "_conn"):
            self._conn = basecrm.Client(access_token=self.config.get("access_token"))
        return self._conn

    def get_records(self, context: dict | None) -> Iterable[dict | tuple[dict, dict]]:
        """Return a generator of row-type dictionary objects."""
        raise NotImplementedError
