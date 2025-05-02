"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_zendesk_sell.tap import TapZendeskSell

TestTapZendeskSell = get_tap_test_class(
    tap_class=TapZendeskSell,
    config={"device_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"},
    suite_config=SuiteConfig(
        max_records_limit=100,
        ignore_no_records=True,
    ),
)
