"""Stream type classes for tap-zendesk_sell."""
from pathlib import Path

SCHEMAS_DIR = Path(__file__).parent.parent / Path("./schemas")

from .accounts import AccountsStream
from .contacts import ContactsStream
from .deal_sources import DealSourcesStream
from .deals import AssociatedContacts, DealsStream
from .lead_sources import LeadSourcesStream
from .lead_unqualified_reasons import LeadUnqualifiedReasonsStream
from .leads import LeadsStream
from .loss_reasons import LossReasonsStream
from .notes import NotesStream
from .orders import LineItemsStream, OrdersStream
from .pipelines import PipelinesStream
from .products import ProductsStream
from .stages import StagesStream
from .sync import SyncStream
from .tags import TagsStream
from .tasks import TasksStream
from .text_messages import TextMessagesStream
from .users import UsersStream
from .visit_outcomes import VisitOutcomesStream
from .visits import VisitsStream

__all___ = [
    "AccountsStream",
    "ContactsStream",
    "DealSourcesStream",
    "AssociatedContacts",
    "DealsStream",
    "LeadSourcesStream",
    "LeadUnqualifiedReasonsStream",
    "LeadsStream",
    "LossReasonsStream",
    "NotesStream",
    "OrdersStream",
    "LineItemsStream",
    "PipelinesStream",
    "ProductsStream",
    "StagesStream",
    "SyncStream",
    "TagsStream",
    "TasksStream",
    "TextMessagesStream",
    "UsersStream",
    "VisitOutcomesStream",
    "VisitsStream",
]
