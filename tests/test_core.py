"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_zendesk_sell.tap import TapZendeskSell

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "device_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",  # Keep existing device_uuid
}


# Run standard built-in tap tests from the SDK:
TestTapZendeskSell = get_tap_test_class(
    tap_class=TapZendeskSell,
    config=SAMPLE_CONFIG,
)
