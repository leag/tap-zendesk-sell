"""Zendesk Sell pipelines stream class."""

from collections.abc import Iterable
from typing import Optional

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class PipelinesStream(ZendeskSellStream):
    """Zendesk Sell pipelines stream class."""

    name = "pipelines"
    primary_keys = ["id"]

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.pipelines.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
            for row in data:
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "pipelines.json"
