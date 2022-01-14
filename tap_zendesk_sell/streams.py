"""Stream type classes for tap-zendesk_sell."""

from pathlib import Path
from typing import Iterable, Optional

from singer_sdk.tap_base import Tap

from tap_zendesk_sell.client import ZendeskSellStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class SyncStream(ZendeskSellStream):
    name = "events"

    def _update_schema(self) -> None:
        """Update the schema for this stream with custom fields."""

        resource_types = [
            "lead",
            "contact",
            "deal",
            "prospect_and_customer",
        ]
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
        for resource_type in resource_types:
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
        if custom_fields_properties:
            self._schema["properties"]["data"]["properties"]["custom_fields"] = {
                "properties": custom_fields_properties
            }

    def __init__(self, tap: Tap):
        super().__init__(tap)
        self._update_schema()

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""

        session = self.conn.sync.start(self.config.get("device_uuid"))
        finished = False
        if session is None or "id" not in session:
            finished = True
        while not finished:
            queue_items = self.conn.sync.fetch(
                self.config.get("device_uuid"), session["id"]
            )
            if not queue_items:
                finished = True
            ack_keys = []
            for item in queue_items:
                ack_keys.append(item["meta"]["sync"]["ack_key"])
                yield {"data": item["data"], "meta": item["meta"]}
            if ack_keys:
                self.conn.sync.ack(self.config.get("device_uuid"), ack_keys)

    schema_filepath = SCHEMAS_DIR / "events.json"
