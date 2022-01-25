"""Zendesk Sell visit outcomes stream class."""
from typing import Iterable, Optional

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class VisitOutcomesStream(ZendeskSellStream):
    """Zendesk Sell visit outcomes stream class."""

    name = "visit_outcomes"
    primary_keys = ["id"]

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.visit_outcomes.list(per_page=200, page=page)
            if not data:
                finished = True
            for row in data:
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "visit_outcomes.json"
