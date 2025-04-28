"""Stream type classes for tap-zendesk-sell."""

from tap_zendesk_sell.streams.accounts import AccountsStream
from tap_zendesk_sell.streams.contacts import ContactsStream
from tap_zendesk_sell.streams.deal_sources import DealSourcesStream
from tap_zendesk_sell.streams.deal_unqualified_reasons import (
    DealUnqualifiedReasonsStream,
)
from tap_zendesk_sell.streams.deals import AssociatedContacts, DealsStream
from tap_zendesk_sell.streams.lead_sources import LeadSourcesStream
from tap_zendesk_sell.streams.lead_unqualified_reasons import (
    LeadUnqualifiedReasonsStream,
)
from tap_zendesk_sell.streams.leads import LeadsStream
from tap_zendesk_sell.streams.loss_reasons import LossReasonsStream
from tap_zendesk_sell.streams.notes import NotesStream
from tap_zendesk_sell.streams.orders import LineItemsStream, OrdersStream
from tap_zendesk_sell.streams.pipelines import PipelinesStream
from tap_zendesk_sell.streams.products import ProductsStream
from tap_zendesk_sell.streams.stages import StagesStream
from tap_zendesk_sell.streams.sync import SyncStream
from tap_zendesk_sell.streams.tags import TagsStream
from tap_zendesk_sell.streams.tasks import TasksStream
from tap_zendesk_sell.streams.text_messages import TextMessagesStream
from tap_zendesk_sell.streams.users import UsersStream
from tap_zendesk_sell.streams.visit_outcomes import VisitOutcomesStream
from tap_zendesk_sell.streams.visits import VisitsStream

__all__ = [
    "AccountsStream",
    "AssociatedContacts",
    "ContactsStream",
    "DealSourcesStream",
    "DealUnqualifiedReasonsStream",
    "DealsStream",
    "LeadSourcesStream",
    "LeadUnqualifiedReasonsStream",
    "LeadsStream",
    "LineItemsStream",
    "LossReasonsStream",
    "NotesStream",
    "OrdersStream",
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
