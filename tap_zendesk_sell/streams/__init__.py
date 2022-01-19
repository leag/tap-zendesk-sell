"""Stream type classes for tap-zendesk_sell."""
from pathlib import Path

from .contacts import ContactsStream
from .deals import DealsStream
from .sync import SyncStream

SCHEMAS_DIR = Path(__file__).parent.parent / Path("./schemas")
