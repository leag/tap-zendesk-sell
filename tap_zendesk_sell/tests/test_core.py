from singer_sdk.testing import get_standard_tap_tests

from tap_zendesk_sell.tap import TapZendeskSell

SAMPLE_CONFIG = {"client_device_uuid": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}


def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapZendeskSell, config=SAMPLE_CONFIG)
    for test in tests:
        test()
