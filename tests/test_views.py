import json

from flasql import views
import mock
import os
from tests.fixtures import app  # noqa
from graphql import GraphQLSyntaxError
from pydantic import ValidationError, BaseModel
from graphql.language.source import Source


class Model(BaseModel):
    name: str


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
        return "string representation"


class UnexpectedError(Exception):
    pass


@mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
def test_format_error_no_details_dev():
    e = MockError()
    formatted = views.format_error(e)

    assert formatted["message"] == "string representation"
    assert "locations" not in formatted


@mock.patch.dict(os.environ, {"ENVIRONMENT": "live"})
def test_format_error_no_details_live():
    e = MockError()
    formatted = views.format_error(e)

    assert formatted["message"] == "Oops! Something went wrong!"
    assert "locations" not in formatted


@mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
def test_format_error_with_message_dev():
    e = MockError(message="bailed out")
    formatted = views.format_error(e)

    assert formatted["message"] == "bailed out"
    assert "locations" not in formatted


@mock.patch.dict(os.environ, {"ENVIRONMENT": "live"})
def test_format_error_with_message_live():
    e = MockError(message="bailed out")
    formatted = views.format_error(e)

    assert formatted["message"] == "Oops! Something went wrong!"
    assert "locations" not in formatted


@mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
def test_format_error_with_one_location_dev():
    locations = [MockLocation(3, 42)]
    e = MockError(message="bailed out", locations=locations)
    formatted = views.format_error(e)

    assert formatted["message"] == "bailed out"
    assert len(formatted["locations"]) == 1
    assert formatted["locations"] == [{"line": 3, "column": 42}]


@mock.patch.dict(os.environ, {"ENVIRONMENT": "live"})
def test_format_error_with_one_location_live():
    locations = [MockLocation(3, 42)]
    e = MockError(message="bailed out", locations=locations)
    formatted = views.format_error(e)

    assert formatted["message"] == "Oops! Something went wrong!"
    assert "locations" not in formatted


@mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
def test_format_error_with_two_locations_dev():
    locations = [MockLocation(3, 42), MockLocation(7, 57)]
    e = MockError(message="bailed out", locations=locations)
    formatted = views.format_error(e)

    assert formatted["message"] == "bailed out"
    assert len(formatted["locations"]) == 2
    assert formatted["locations"] == [
        {"line": 3, "column": 42},
        {"line": 7, "column": 57},
    ]


@mock.patch.dict(os.environ, {"ENVIRONMENT": "live"})
def test_format_error_with_two_locations_live():
    locations = [MockLocation(3, 42), MockLocation(7, 57)]
    e = MockError(message="bailed out", locations=locations)
    formatted = views.format_error(e)

    assert formatted["message"] == "Oops! Something went wrong!"
    assert "locations" not in formatted


def test_graphqlresult_to_response(app):  # noqa
    result = views.GraphQLResult({"foo": "bar"})
    resp = result.to_response()
    data = json.loads(resp.data)

    assert data == {"foo": "bar"}
    assert resp.status_code == 200
    assert resp.mimetype == "application/json"


@mock.patch.dict(os.environ, {"ENVIRONMENT": "live"})
def test_format_error_handles_graphqlsyntaxerror(monkeypatch):
    source = Source("GraphQLSyntaxError occurred")
    error = GraphQLSyntaxError(source, position=0, description="GraphQLSyntaxError occurred")
    formatted = views.format_error(error)

    assert formatted["message"] == str(error)
    assert "locations" not in formatted


def test_format_error_handles_unexpected_errors(monkeypatch):
    formatted = views.format_error(UnexpectedError("Unexpected error occurred"))

    assert formatted["message"] == "Oops! Something went wrong!"
    assert "locations" not in formatted


@mock.patch.dict(os.environ, {"ENVIRONMENT": "live"})
def test_format_error_handles_validationerror():
    try:
        Model(name=None)  # This will raise a ValidationError
    except ValidationError as e:
        formatted = views.format_error(e)
        assert "1 validation error for Model" in formatted["message"]
        assert "none is not an allowed value" in formatted["message"]
        assert "locations" not in formatted
