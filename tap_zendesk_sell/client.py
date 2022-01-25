"""Zendesk Sell Base Stream class."""

from typing import Any, Dict, Iterable, Optional, Tuple, Union

import basecrm
from singer_sdk import typing as th
from singer_sdk.streams import Stream
from singer_sdk.tap_base import Tap


class ZendeskSellStream(Stream):
    """Zendesk Sell sync stream class."""

    address_type = th.ObjectType(
        th.Property(
            "line1",
            th.StringType,
            description="Line 1 of the address e.g. number, street, suite, apt #, etc.",  # noqa
        ),
        th.Property("city", th.StringType, description="City name."),
        th.Property(
            "postal_code", th.StringType, description="Zip code or equivalent."
        ),
        th.Property("state", th.StringType, description="State name."),
        th.Property("country", th.StringType, description="Country name."),
    )

    custom_field_type: Dict[str, Any] = {
        "address": address_type,
        "bool": th.StringType,
        "date": th.StringType,
        "datetime": th.DateTimeType,
        "email": th.StringType,
        "list": th.StringType,
        "multi_select_list": th.ArrayType(th.StringType),
        "number": th.StringType,
        "phone": th.StringType,
        "string": th.StringType,
        "text": th.StringType,
        "url": th.StringType,
    }
    resource_types = {
        "deal",
        "contact",
        "lead",
        "prospect_and_customer",
    }

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
        assert resource_type_set.issubset(
            self.resource_types
        ), f"{resource_type_set} is not a valid resource type set"

        custom_fields_properties = {}
        for resource_type in resource_type_set:
            _, _, data = self.conn.http_client.get(
                "/{resource_type}/custom_fields".format(resource_type=resource_type)
            )
            for custom_field in data:
                if custom_field["name"] not in custom_fields_properties:
                    custom_fields_properties[
                        custom_field["name"]
                    ] = self.custom_field_type[custom_field["type"]].type_dict
                else:
                    if (
                        custom_fields_properties[custom_field["name"]]
                        != self.custom_field_type[custom_field["type"]].type_dict
                    ):
                        raise ValueError("Custom field name conflict")
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
