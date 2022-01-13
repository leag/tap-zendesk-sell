"""REST client handling, including ZendeskSellStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable
from singer_sdk.streams import Stream
import basecrm
from singer_sdk.tap_base import Tap


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ZendeskSellStream(Stream):
    """Zendesk Sell sync stream class."""

    def __init__(self, tap: Tap):
        super().__init__(tap)
        self.conn = basecrm.Client(access_token=self.config.get("access_token"))
