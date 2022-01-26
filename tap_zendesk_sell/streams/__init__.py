"""Stream type classes for tap-zendesk-sell."""
from pathlib import Path

SCHEMAS_DIR: Path = Path(__file__).parent.parent / Path("./schemas")

from .accounts import AccountsStream  # noqa
from .contacts import ContactsStream  # noqa
from .deal_sources import DealSourcesStream  # noqa
from .deals import AssociatedContacts, DealsStream  # noqa
from .lead_sources import LeadSourcesStream  # noqa
from .lead_unqualified_reasons import LeadUnqualifiedReasonsStream  # noqa
from .leads import LeadsStream  # noqa
from .loss_reasons import LossReasonsStream  # noqa
from .notes import NotesStream  # noqa
from .orders import LineItemsStream, OrdersStream  # noqa
from .pipelines import PipelinesStream  # noqa
from .products import ProductsStream  # noqa
from .stages import StagesStream  # noqa
from .sync import SyncStream  # noqa
from .tags import TagsStream  # noqa
from .tasks import TasksStream  # noqa
from .text_messages import TextMessagesStream  # noqa
from .users import UsersStream  # noqa
from .visit_outcomes import VisitOutcomesStream  # noqa
from .visits import VisitsStream  # noqa

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
