"""Zendesk Sell Base Stream class."""

from typing import Dict, Iterable, Optional, Tuple, Union

import basecrm
from singer_sdk.streams import Stream
from singer_sdk.tap_base import Tap


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

    custom_field_type: Dict[str, Dict] = {
        "address": {
            "type": ["object", "null"],
            "properties": address_properties,
        },
        "bool": {"type": ["boolean", "null"]},
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

    def _update_schema(self, resource_type_set: set = None) -> dict:
        """Update the schema for this stream with custom fields."""
        if resource_type_set is None:
            resource_type_set = {
                "deal",
                "contact",
                "lead",
                "prospect_and_customer",
            }
        if not resource_type_set.issubset(self.resource_types):
            raise ValueError(f"{resource_type_set} is not a valid resource type set")

        custom_fields_properties = {}
        for resource_type in resource_type_set:
            _, _, data = self.conn.http_client.get(
                "/{resource_type}/custom_fields".format(resource_type=resource_type)
            )
            for custom_field in data:
                type_dict = self.custom_field_type[custom_field["type"]]
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

    def __init__(self, tap: Tap):
        """Initialize the stream."""
        super().__init__(tap)
        self.conn = basecrm.Client(access_token=self.config.get("access_token"))

    def get_records(
        self, context: Optional[dict]
    ) -> Iterable[Union[dict, Tuple[dict, dict]]]:
        """Return a generator of row-type dictionary objects."""
        pass
