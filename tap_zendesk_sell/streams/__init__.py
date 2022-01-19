"""Stream type classes for tap-zendesk_sell."""
from pathlib import Path
SCHEMAS_DIR = Path(__file__).parent.parent / Path("./schemas")

from .contacts import ContactsStream
from .deals import DealsStream
from .sync import SyncStream
from .leads import LeadsStream


__all___ = [
    "ContactsStream",
    "DealsStream",
    "SyncStream",
    "LeadsStream",
]
