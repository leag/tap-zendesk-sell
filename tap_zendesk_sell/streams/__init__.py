"""Stream type classes for tap-zendesk_sell."""
from pathlib import Path
SCHEMAS_DIR = Path(__file__).parent.parent / Path("./schemas")

from .accounts import AccountsStream
from .contacts import ContactsStream
from .deals import DealsStream, AssociatedContacts
from .sync import SyncStream
from .leads import LeadsStream
from .deal_sources import DealSourcesStream

__all___ = [
    "AccountsStream",
    "ContactsStream",
    "DealsStream",
    "AssociatedContacts",
    "SyncStream",
    "LeadsStream",
    "DealSourcesStream",
]
