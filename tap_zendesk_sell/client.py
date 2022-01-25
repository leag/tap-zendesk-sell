"""Zendesk Sell Base Stream class."""

from singer_sdk.streams import Stream
import basecrm
from singer_sdk.tap_base import Tap
from singer_sdk import typing as th


class ZendeskSellStream(Stream):
    """Zendesk Sell sync stream class."""

    @staticmethod
    def address_schema(
        address: str = "address", description: str = "Address object.", **kwargs
    ) -> th.Property:
        """Return an address object schema."""
        return th.Property(
            address,
            th.ObjectType(
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
            ),
            description=description,
            **kwargs,
        )

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
            "address": self.address_schema(),
            "bool": th.Property("bool", th.BooleanType),
            "date": th.Property("date", th.StringType),
            "datetime": th.Property("datetime", th.DateTimeType),
            "email": th.Property("email", th.StringType),
            "list": th.Property("list", th.StringType),
            "multi_select_list": th.Property(
                "multi_select_list", th.ArrayType(th.StringType)
            ),
            "number": th.Property("number", th.StringType),
            "phone": th.Property("phone", th.StringType),
            "string": th.Property("string", th.StringType),
            "text": th.Property("text", th.StringType),
            "url": th.Property("url", th.StringType),
        }
        custom_fields_properties = {}
        for resource_type in resource_type_set:
            _, _, data = self.conn.http_client.get(
                "/{resource_type}/custom_fields".format(resource_type=resource_type)
            )
            for custom_field in data:
                if custom_field["name"] not in custom_fields_properties:
                    custom_fields_properties[custom_field["name"]] = custom_field_type[
                        custom_field["type"]
                    ].to_dict()
                else:
                    raise ValueError(
                        f"Custom field {custom_field['name']} already exists."
                    )

        return custom_fields_properties

    def __init__(self, tap: Tap):
        super().__init__(tap)
        self.conn = basecrm.Client(access_token=self.config.get("access_token"))
