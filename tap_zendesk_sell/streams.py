"""Stream type classes for tap-zendesk_sell."""

from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_zendesk_sell.client import ZendeskSellStream
from singer_sdk.tap_base import Tap



class SyncStream(ZendeskSellStream):
    name = "sync"
 
    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""

        session = self.conn.sync.start(self.config.get("device_uuid"))
        finished = False
        if session is None or "id" not in session:
            finished = True
        while not finished:
            queue_items = self.conn.sync.fetch(self.config.get("device_uuid"), session['id'])
            if not queue_items:
                finished = True
            ack_keys = []
            for item in queue_items:
                ack_keys.append(item['meta']['sync']['ack_key'])
                yield {"data": item['data'], "meta": item['meta']}
            if ack_keys:
                self.conn.sync.ack(self.config.get("device_uuid"), ack_keys)

    schema = th.PropertiesList(
        th.Property("meta", th.StringType),
        th.Property("data", th.StringType),
    ).to_dict()
