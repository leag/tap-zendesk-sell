"""Zendesk Sell Base Stream class."""

from singer_sdk.streams import Stream
import basecrm
from singer_sdk.tap_base import Tap
from singer_sdk import typing as th

class ZendeskSellStream(Stream):
    """Zendesk Sell sync stream class."""

    def _update_schema(
        self,
        resource_type_set: set = {
            "deal",
            "contact",
            "lead",
            "prospect_and_customer",
        },
    ) -> dict:
        """Update the schema for this stream with custom fields."""

        resource_types = {
            "deal",
            "contact",
            "lead",
            "prospect_and_customer",
        }
        assert resource_type_set.issubset(
            resource_types
        ), f"{resource_type_set} is not a valid resource type set"

        custom_field_type = {
            "address": "object",
            "bool": "string",
            "date": "string",
            "datetime": "string",
            "email": "string",
            "list": "string",
            "multi_select_list": "array",
            "number": "string",
            "phone": "string",
            "string": "string",
            "text": "string",
            "url": "string",
        }
        address_type = {
            "address_line_1": ["null", "string"],
            "city": ["null", "string"],
            "postal_code": ["null", "string"],
            "state": ["null", "string"],
            "country": ["null", "string"],
        }
        custom_fields_properties = {}
        for resource_type in resource_type_set:
            _, _, data = self.conn.http_client.get(
                "/{resource_type}/custom_fields".format(resource_type=resource_type)
            )
            for custom_field in data:
                if custom_field["type"] == "address":
                    if not custom_fields_properties.get(custom_field["name"]):
                        custom_fields_properties[custom_field["name"]] = {
                            "type": ["null", "object"],
                            "properties": address_type,
                        }
                    else:
                        if (
                            "object"
                            not in custom_fields_properties[custom_field["name"]][
                                "type"
                            ]
                        ):
                            custom_fields_properties[custom_field["name"]][
                                "type"
                            ].append("object")
                        for key in address_type:
                            if (
                                key
                                not in custom_fields_properties[custom_field["name"]][
                                    "properties"
                                ]
                            ):
                                custom_fields_properties[custom_field["name"]][
                                    "properties"
                                ][key] = address_type[key]
                elif custom_field["type"] == "multi_select_list":
                    if not custom_fields_properties.get(custom_field["name"]):
                        custom_fields_properties[custom_field["name"]] = {
                            "type": ["null", "array"],
                            "items": {"type": "string"},
                        }
                    else:
                        if (
                            "array"
                            not in custom_fields_properties[custom_field["name"]][
                                "type"
                            ]
                        ):
                            custom_fields_properties[custom_field["name"]][
                                "type"
                            ].append("array")
                        custom_fields_properties[custom_field["name"]]["items"] = {
                            "type": "string"
                        }
                elif custom_field["type"] in custom_field_type:
                    if not custom_fields_properties.get(custom_field["name"]):
                        custom_fields_properties[custom_field["name"]] = {
                            "type": ["null", custom_field_type[custom_field["type"]]],
                        }
                    else:
                        if (
                            custom_field_type[custom_field["type"]]
                            not in custom_fields_properties[custom_field["name"]][
                                "type"
                            ]
                        ):
                            custom_fields_properties[custom_field["name"]][
                                "type"
                            ].append(custom_field_type[custom_field["type"]])
        return custom_fields_properties

    @staticmethod
    def address_schema(
        address: str = "address", description: str = "Address object."
    ) -> th.Property:
        """Return an address object schema."""
        return th.Property(
            address,
            th.ObjectType(
                th.Property(
                    "line1",
                    th.StringType,
                    description="Line 1 of the address e.g. number, street, suite, apt #, etc.",
                ),
                th.Property("city", th.StringType, description="City name."),
                th.Property(
                    "postal_code", th.StringType, description="Zip code or equivalent."
                ),
                th.Property("state", th.StringType, description="State name."),
                th.Property("country", th.StringType, description="Country name."),
            ),
            description=description,
        )

    def __init__(self, tap: Tap):
        super().__init__(tap)
        self.conn = basecrm.Client(access_token=self.config.get("access_token"))
