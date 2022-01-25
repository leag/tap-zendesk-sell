"""Zendesk Sell loss reasons stream class."""
from typing import Iterable, Optional

from tap_zendesk_sell.client import ZendeskSellStream
from tap_zendesk_sell.streams import SCHEMAS_DIR


class LossReasonsStream(ZendeskSellStream):
    """Zendesk Sell loss reasons stream class."""

    name = "loss_reasons"
    primary_keys = ["id"]

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Return a generator of row-type dictionary objects."""
        finished = False
        page = 1
        while not finished:
            data = self.conn.loss_reasons.list(per_page=100, page=page, sort_by="id")
            if not data:
                finished = True
            for row in data:
                yield row
            page += 1

    schema_filepath = SCHEMAS_DIR / "loss_reasons.json"
