import json

from flasql import views


class MockLocation(object):
    def __init__(self, line, column):
        self.line = line
        self.column = column


class MockError(object):
    def __init__(self, message=None, locations=None):
        if message is not None:
            self.message = message
        if locations is not None:
            self.locations = locations

    def __str__(self):
        return 'string representation'


def test_format_error_no_details():
    e = MockError()
    formatted = views.format_error(e)
    assert formatted['message'] == 'string representation'
    assert 'locations' not in formatted


def test_format_error_with_message():
    e = MockError(message='bailed out')
    formatted = views.format_error(e)
    assert formatted['message'] == 'bailed out'
    assert 'locations' not in formatted


def test_format_error_with_one_location():
    locations = [MockLocation(3, 42)]
    e = MockError(message='bailed out', locations=locations)
    formatted = views.format_error(e)
    assert formatted['message'] == 'bailed out'
    assert len(formatted['locations']) == 1
    assert formatted['locations'] == [{'line': 3, 'column': 42}]


def test_format_error_with_two_locations():
    locations = [MockLocation(3, 42), MockLocation(7, 57)]
    e = MockError(message='bailed out', locations=locations)
    formatted = views.format_error(e)
    assert formatted['message'] == 'bailed out'
    assert len(formatted['locations']) == 2
    assert formatted['locations'] == [
        {'line': 3, 'column': 42},
        {'line': 7, 'column': 57},
    ]


def test_graphqlresult_to_response():
    result = views.GraphQLResult({'foo': 'bar'})
    resp = result.to_response()
    data = json.loads(resp.data)
    assert data == {'foo': 'bar'}
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
