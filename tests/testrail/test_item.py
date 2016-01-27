import pytest

from testrail_reporter.testrail.client import Item


@pytest.mark.parametrize('class_name, expected_name', [
    ('Result', 'result'),
    ('TestPlanEntry', 'test_plan_entry'),
])
def test_item_name(class_name, expected_name):
    klass = type(class_name, (Item,), {})
    assert klass._api_name() == expected_name
