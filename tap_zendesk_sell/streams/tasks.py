"""Zendesk Sell tasks stream class."""
from typing import Iterable, Optional

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class TasksStream(ZendeskSellStream):
    """Zendesk Sell tasks stream class."""

    name = "tasks"
    primary_keys = ["id"]

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.tasks.list(per_page=100, page=page, sort_by="updated_at")
            if not data:
                finished = True
            for row in data:
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "tasks.json"
